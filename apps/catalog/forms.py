from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError

from .dicts import (DESCRIPTION_LIMIT, PART_TYPES_AUTO, PART_TYPES_MOTO,
                    CAR_TIRE_WIDTHS, CAR_TIRE_PROFILES, CAR_TIRE_DIAMETERS,
                    RIM_WIDTHS, RIM_DIAMETERS,
                    BOLT_COUNTS, PCD_DIAMETERS,
                    MOTO_TIRE_WIDTHS, MOTO_TIRE_PROFILES,
                    MOTO_TIRE_DIAMETERS, MOTO_RIM_DIAMETERS,
                    WHEEL_FORM_FIELDS)

from .models import AutoPart, MotoPart, Wheel, PartPhoto, Category

DESCRIPTION_LIMIT = 3000


class MultiFileInput(forms.FileInput):
    """FileInput с multiple: атрибут ставится после инициализации,
    иначе Django 5+ кидает ValueError."""
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs["multiple"] = True


class BasePartForm(forms.ModelForm):
    photos = forms.FileField(
        label="Фотографии",
        widget=MultiFileInput(),
        required=False,
        help_text="Минимум одна. Первое фото — главное.",
    )

    # подклассы переопределяют, какие категории показывать (auto/moto/None)
    category_scope = "auto"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # описания с живым лимитом
        self.fields["description"].widget.attrs.update(
            {"maxlength": DESCRIPTION_LIMIT, "rows": 4})
        # фильтруем категории по scope подкласса (если поле есть)
        if "category" in self.fields and self.category_scope:
            self.fields["category"].queryset = Category.objects.filter(
                scope=self.category_scope)

    def clean_description(self):
        d = self.cleaned_data.get("description", "")
        if len(d) > DESCRIPTION_LIMIT:
            raise ValidationError(
                f"Описание длиннее {DESCRIPTION_LIMIT} символов (лимит Авито)")
        return d

    def clean(self):
        cleaned = super().clean()
        # при редактировании можно не перекладывать фото: они уже у товара
        if not self.instance.pk and not self.files.getlist("photos"):
            self.add_error("photos", "Загрузите хотя бы одно фото")
        return cleaned

    def save(self, commit=True):
        item = super().save(commit)
        for f in self.files.getlist("photos"):
            PartPhoto.objects.create(item=item, image=f)
        return item


class AutoPartForm(BasePartForm):
    """Совместимость — только через справочник CarModel."""
    class Meta:
        model = AutoPart
        fields = ("name", "category", "part_type", "compatible_cars",
                  "engine_code", "location_note", "condition", "brand", "oem",
                  "price", "stock", "description", "is_active")
        widgets = {"compatible_cars": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["part_type"] = forms.ChoiceField(
            label="Тип детали", choices=[(v, v) for v in PART_TYPES_AUTO])


class MotoPartForm(BasePartForm):
    """Совместимость — только через справочник MotoModel."""
    category_scope = "moto"

    class Meta:
        model = MotoPart
        fields = ("name", "category", "part_type", "compatible_moto",
                  "year_from", "year_to", "condition", "brand", "oem",
                  "price", "stock", "description", "is_active")
        widgets = {"compatible_moto": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["part_type"] = forms.ChoiceField(
            label="Тип детали", choices=[(v, v) for v in PART_TYPES_MOTO])


class WheelForm(BasePartForm):
    category_scope = None  # у Wheel нет поля category — фильтровать нечего

    class Meta:
        model = Wheel
        fields = ("name", "vehicle_kind", "product_form", "model_name",
                  "tire_width", "tire_profile", "tire_diameter", "season",
                  "tread_remain", "rim_width", "rim_diameter", "rim_type",
                  "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore",
                  "items_count", "fitment", "condition", "brand", "oem",
                  "price", "stock", "description", "is_active")
        widgets = {"fitment": forms.CheckboxSelectMultiple}

    # все «специфичные» поля, которые могут скрываться
    SPECIFIC_FIELDS = (
        "tire_width", "tire_profile", "tire_diameter", "season", "tread_remain",
        "rim_width", "rim_diameter", "rim_type",
        "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # определяем product_form: из POST, из instance или из initial
        pf = (
            self.data.get("product_form")
            or (self.instance.product_form if self.instance and self.instance.pk else None)
            or self.initial.get("product_form")
        )
                # определяем vehicle_kind: из POST, из instance или из initial
        vk = (
            self.data.get("vehicle_kind")
            or (self.instance.vehicle_kind if self.instance and self.instance.pk else None)
            or self.initial.get("vehicle_kind")
            or "car"  # по умолчанию — авто
        )
        self._apply_choices(vk)
        self._apply_visibility(pf)

    def _apply_choices(self, vehicle_kind):
        """Подменяет свободные числовые поля на ChoiceField из словарей."""
        is_car = (vehicle_kind == "car")

        tire_widths   = CAR_TIRE_WIDTHS   if is_car else MOTO_TIRE_WIDTHS
        tire_profiles = CAR_TIRE_PROFILES if is_car else MOTO_TIRE_PROFILES
        tire_diams    = CAR_TIRE_DIAMETERS if is_car else MOTO_TIRE_DIAMETERS
        rim_diams     = RIM_DIAMETERS     if is_car else MOTO_RIM_DIAMETERS

        # (value, label) — value как строка, чтобы совпадало с тем, что придёт из POST
        def pairs(seq):
            return [(str(x), str(x)) for x in seq]

        # ширина шины
        self.fields["tire_width"] = forms.ChoiceField(
            label=self.fields["tire_width"].label,
            choices=[("", "—")] + pairs(tire_widths),
            required=False,
        )
        # профиль
        self.fields["tire_profile"] = forms.ChoiceField(
            label=self.fields["tire_profile"].label,
            choices=[("", "—")] + pairs(tire_profiles),
            required=False,
        )
        # диаметр шины
        self.fields["tire_diameter"] = forms.ChoiceField(
            label=self.fields["tire_diameter"].label,
            choices=[("", "—")] + pairs(tire_diams),
            required=False,
        )
        # ширина диска
        self.fields["rim_width"] = forms.ChoiceField(
            label=self.fields["rim_width"].label,
            choices=[("", "—")] + pairs(RIM_WIDTHS),
            required=False,
        )
        # диаметр диска
        self.fields["rim_diameter"] = forms.ChoiceField(
            label=self.fields["rim_diameter"].label,
            choices=[("", "—")] + pairs(rim_diams),
            required=False,
        )
        # количество болтов
        self.fields["pcd_bolt_count"] = forms.ChoiceField(
            label=self.fields["pcd_bolt_count"].label,
            choices=[("", "—")] + pairs(BOLT_COUNTS),
            required=False,
        )
        # PCD
        self.fields["pcd_diameter"] = forms.ChoiceField(
            label=self.fields["pcd_diameter"].label,
            choices=[("", "—")] + pairs(PCD_DIAMETERS),
            required=False,
        )   

    def _apply_visibility(self, product_form):
        if product_form not in WHEEL_FORM_FIELDS:
            return
        conf = WHEEL_FORM_FIELDS[product_form]
        show = set(conf["show"])
        required = set(conf["required"])
        for name in self.SPECIFIC_FIELDS:
            if name not in self.fields:
                continue
            if name in show:
                # оставляем видимым, required — по словарю
                self.fields[name].required = name in required
            else:
                # скрываем и снимаем required
                self.fields[name].widget = forms.HiddenInput()
                self.fields[name].required = False

    # какие поля — числовые (даже если сейчас ChoiceField)
    NUMERIC_FIELDS = {
        "tire_width", "tire_profile", "tire_diameter",
        "rim_width", "rim_diameter",
        "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore",
        "tread_remain",
    }

    def clean(self):
        cleaned = super().clean()
        pf = cleaned.get("product_form") or self.data.get("product_form")

        # 1) скрытые поля обнуляем
        if pf in WHEEL_FORM_FIELDS:
            show = set(WHEEL_FORM_FIELDS[pf]["show"])
            for name in self.SPECIFIC_FIELDS:
                if name not in show and name in cleaned:
                    if name in self.NUMERIC_FIELDS:
                        cleaned[name] = None
                    else:
                        cleaned[name] = ""

        # 2) пустые строки в числовых -> None, непустые -> приводим к числу
        for name in self.NUMERIC_FIELDS:
            if name not in cleaned:
                continue
            val = cleaned[name]
            if val in ("", None):
                cleaned[name] = None
            else:
                # ChoiceField вернул строку — приводим к типу модели
                try:
                    if name in ("rim_width", "pcd_diameter", "center_bore", "tread_remain"):
                        cleaned[name] = Decimal(val)
                    else:
                        cleaned[name] = int(val)
                except (TypeError, ValueError, InvalidOperation):
                    self.add_error(name, "Некорректное значение")
        return cleaned