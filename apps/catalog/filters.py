import django_filters as filters

from .dicts import (
    CONDITIONS, PRODUCT_FORMS, VEHICLE_KINDS, SEASONS, RIM_TYPES,
    CAR_TIRE_WIDTHS, CAR_TIRE_PROFILES, CAR_TIRE_DIAMETERS,
    RIM_WIDTHS, RIM_DIAMETERS, BOLT_COUNTS, PCD_DIAMETERS,
    MOTO_TIRE_WIDTHS, MOTO_TIRE_PROFILES,
    MOTO_TIRE_DIAMETERS, MOTO_RIM_DIAMETERS,
)
from .models import AutoPart, MotoPart, Wheel


def _choices(seq):
    """Список строк -> [(v, v)] с пустым вариантом '—'."""
    return [("", "—")] + [(str(x), str(x)) for x in seq]


class BasePartFilter(filters.FilterSet):
    """Общие фильтры для всех типов деталей."""
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte", label="Цена от")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte", label="Цена до")
    condition = filters.ChoiceFilter(choices=CONDITIONS, label="Состояние")
    brand = filters.CharFilter(lookup_expr="icontains", label="Бренд")
    in_stock = filters.BooleanFilter(method="filter_in_stock", label="В наличии")

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset


class AutoPartFilter(BasePartFilter):
    category = filters.CharFilter(field_name="category__name", lookup_expr="icontains", label="Категория")
    part_type = filters.CharFilter(lookup_expr="icontains", label="Тип детали")
    compatible_car = filters.CharFilter(method="filter_compatible_car", label="Совместимость")

    class Meta:
        model = AutoPart
        fields = []

    def filter_compatible_car(self, queryset, name, value):
        if value:
            return queryset.filter(compatible_cars__make__icontains=value) | \
                   queryset.filter(compatible_cars__model__icontains=value)
        return queryset


class MotoPartFilter(BasePartFilter):
    category = filters.CharFilter(field_name="category__name", lookup_expr="icontains", label="Категория")
    part_type = filters.CharFilter(lookup_expr="icontains", label="Тип детали")
    year = filters.NumberFilter(method="filter_year", label="Год")

    class Meta:
        model = MotoPart
        fields = []

    def filter_year(self, queryset, name, value):
        if value:
            return queryset.filter(year_from__lte=value, year_to__gte=value)
        return queryset


class WheelFilter(BasePartFilter):
    vehicle_kind = filters.ChoiceFilter(choices=VEHICLE_KINDS, label="Тип техники")
    product_form = filters.ChoiceFilter(choices=PRODUCT_FORMS, label="Тип товара")
    season = filters.ChoiceFilter(choices=SEASONS, label="Сезонность")
    rim_type = filters.ChoiceFilter(choices=RIM_TYPES, label="Тип диска")

    # числовые — NumberFilter (сравнивает как число)
    tire_width = filters.NumberFilter(field_name="tire_width", lookup_expr="exact", label="Ширина шины")
    tire_profile = filters.NumberFilter(field_name="tire_profile", lookup_expr="exact", label="Профиль")
    tire_diameter = filters.NumberFilter(field_name="tire_diameter", lookup_expr="exact", label="Диаметр шины")
    rim_width = filters.NumberFilter(field_name="rim_width", lookup_expr="exact", label="Ширина диска")
    rim_diameter = filters.NumberFilter(field_name="rim_diameter", lookup_expr="exact", label="Диаметр диска")
    pcd_bolt_count = filters.NumberFilter(field_name="pcd_bolt_count", lookup_expr="exact", label="Кол-во болтов")
    pcd_diameter = filters.NumberFilter(field_name="pcd_diameter", lookup_expr="exact", label="PCD")

    class Meta:
        model = Wheel
        fields = []