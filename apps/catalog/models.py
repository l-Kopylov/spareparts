from django.db import models


from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .dicts import (SCOPE_CHOICES, CONDITIONS, VEHICLE_KINDS,
                    PRODUCT_FORMS, SEASONS, RIM_TYPES, WHEEL_FORM_FIELDS) 



# ---------- Справочники ----------

class Category(models.Model):
    SCOPE = [("auto", "Авто"), ("moto", "Мото")]
    name = models.CharField("Категория", max_length=100)  # без unique=True
    scope = models.CharField("Тип техники", max_length=10, choices=SCOPE)

    class Meta:
        verbose_name = "Категория запчастей"
        verbose_name_plural = "Категории запчастей"
        unique_together = ("name", "scope")

    def __str__(self):
        return f"{self.name} ({self.get_scope_display()})"

class CarModel(models.Model):
    make = models.CharField("Марка", max_length=50)
    model = models.CharField("Модель", max_length=100)
    generation = models.CharField("Поколение", max_length=150, blank=True)

    class Meta:
        verbose_name = "Модель авто"
        verbose_name_plural = "Модели авто"
        unique_together = ("make", "model", "generation")

    def __str__(self):
        return " | ".join(x for x in (self.make, self.model, self.generation) if x)


class MotoModel(models.Model):
    make = models.CharField("Марка", max_length=50)
    model = models.CharField("Модель", max_length=100)

    class Meta:
        verbose_name = "Модель мото"
        verbose_name_plural = "Модели мото"
        unique_together = ("make", "model")

    def __str__(self):
        return f"{self.make} {self.model}"


# ---------- Фото (общая модель для всех сущностей) ----------

class PartPhoto(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    image = models.ImageField("Фото", upload_to="products/")
    sort = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort", "id"]

    def __str__(self):
        return f"Фото #{self.pk}"


# ---------- Общая база ----------

class PartBase(models.Model):
    CONDITION = [("new", "Новое"), ("used", "Б/у")]

    name = models.CharField("Наименование", max_length=200)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена, руб.", max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField("Остаток", default=0)
    condition = models.CharField("Состояние", max_length=10, choices=CONDITION)
    brand = models.CharField("Производитель", max_length=100, blank=True)
    oem = models.CharField("ОЕМ-артикул", max_length=100, blank=True)
    is_active = models.BooleanField("Показывать на витрине", default=True)
    photos = GenericRelation(PartPhoto, related_query_name="part")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # Серия засева: откуда пришёл товар (ИП Пупкин, ООО Рога и Копыта 2)
    batch_name = models.CharField(
        "Серия засева", max_length=200, blank=True, db_index=True,
        help_text="Источник/поставщик, например: ИП Пупкин, ООО Рога и Копыта 2"
    )
    # Внешний ID для upsert при импорте (Id из Авито)
    external_id = models.CharField(
        "Внешний ID", max_length=100, blank=True, db_index=True,
        help_text="Id из фида Авито, для обновления без дублей"
    )    


# ---------- Деталь для авто ----------

class AutoPart(PartBase):
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 limit_choices_to={"scope": "auto"},
                                 verbose_name="Категория детали")
    part_type = models.CharField("Тип детали", max_length=100)
    compatible_cars = models.ManyToManyField(CarModel, verbose_name="Совместимые авто",
                                             blank=True)
    engine_code = models.CharField("Код двигателя", max_length=50, blank=True)
    location_note = models.CharField("Расположение / примечание", max_length=200, blank=True)

    class Meta:
        verbose_name = "Деталь для авто"
        verbose_name_plural = "Детали для авто"

    def __str__(self):
        return self.name


# ---------- Деталь для мото ----------

class MotoPart(PartBase):
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 limit_choices_to={"scope": "moto"},
                                 verbose_name="Категория детали")
    part_type = models.CharField("Тип детали", max_length=100)
    compatible_moto = models.ManyToManyField(MotoModel, verbose_name="Совместимая мототехника",
                                             blank=True)
    year_from = models.PositiveSmallIntegerField("Год от", null=True, blank=True)
    year_to = models.PositiveSmallIntegerField("Год до", null=True, blank=True)

    class Meta:
        verbose_name = "Деталь для мото"
        verbose_name_plural = "Детали для мото"

    def __str__(self):
        return self.name


# ---------- Колёса и шины ----------

class Wheel(PartBase):


    vehicle_kind = models.CharField("Тип техники", max_length=10, choices=VEHICLE_KINDS)
    product_form = models.CharField("Тип товара", max_length=10, choices=PRODUCT_FORMS)
    model_name = models.CharField("Модель", max_length=100, blank=True)

    # --- параметры шины (обязательны для «Шина» и «Колесо в сборе») ---
    tire_width = models.PositiveSmallIntegerField("Ширина шины, мм", null=True, blank=True)
    tire_profile = models.PositiveSmallIntegerField("Профиль, %", null=True, blank=True)
    tire_diameter = models.PositiveSmallIntegerField("Диаметр, дюйм", null=True, blank=True)
    season = models.CharField("Сезонность", max_length=20, choices=SEASONS, blank=True)
    tread_remain = models.DecimalField("Остаток протектора, мм", max_digits=3,
                                       decimal_places=1, null=True, blank=True)

    # --- параметры диска (обязательны для «Диск» и «Колесо в сборе») ---
    rim_width = models.DecimalField("Ширина диска, J", max_digits=4, decimal_places=1,
                                    null=True, blank=True)
    rim_diameter = models.PositiveSmallIntegerField("Диаметр диска, дюйм", null=True, blank=True)
    rim_type = models.CharField("Тип диска", max_length=10, choices=RIM_TYPES, blank=True)
    pcd_bolt_count = models.PositiveSmallIntegerField("Кол-во крепёжных отверстий", null=True,
                                                      blank=True)
    pcd_diameter = models.DecimalField("PCD, мм", max_digits=5, decimal_places=1, null=True,
                                       blank=True)
    offset_et = models.IntegerField("Вылет ET", null=True, blank=True)
    center_bore = models.DecimalField("DIA (ступица), мм", max_digits=5, decimal_places=1,
                                      null=True, blank=True)

    items_count = models.PositiveSmallIntegerField("Количество в комплекте", default=1)
    fitment = models.ManyToManyField(CarModel, verbose_name="Подходит на авто", blank=True)

    class Meta:
        verbose_name = "Колесо/шина/диск"
        verbose_name_plural = "Колёса и шины"

    def clean(self):
        errors = {}
        conf = WHEEL_FORM_FIELDS.get(self.product_form, {})
        required = conf.get("required", [])

        for f in required:
            if getattr(self, f) in (None, ""):
                errors[f] = "Обязательное поле для этого типа товара"

        # Спец-правило: для б/у шины/комплекта обязателен остаток протектора
        if (self.product_form in ("tire", "set")
                and self.condition == "used"
                and self.tread_remain is None):
            errors["tread_remain"] = "Для Б/у обязательно"

        if errors:
            raise ValidationError(errors)
        errors = {}
        if self.product_form in ("tire", "set"):
            for f in ("tire_width", "tire_profile", "tire_diameter", "season"):
                if not getattr(self, f):
                    errors[f] = "Обязательно для шины и колеса в сборе"
            if self.condition == "used" and self.tread_remain is None:
                errors["tread_remain"] = "Для Б/у обязательно"
        if self.product_form in ("rim", "set"):
            for f in ("rim_diameter", "rim_type", "pcd_bolt_count", "pcd_diameter", "offset_et"):
                if not getattr(self, f):
                    errors[f] = "Обязательно для диска и колеса в сборе"
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name
