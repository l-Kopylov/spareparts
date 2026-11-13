import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.catalog.models import Category, Wheel
from apps.catalog.tests.factories import (
    CategoryFactory, WheelFactory, AutoPartFactory, MotoPartFactory,
)


# ---------- Category ----------

@pytest.mark.django_db
def test_category_unique_together():
    Category.objects.create(name="Двигатель", scope="auto")
    Category.objects.create(name="Двигатель", scope="moto")  # ок
    assert Category.objects.filter(name="Двигатель").count() == 2


@pytest.mark.django_db
def test_category_same_scope_duplicate():
    Category.objects.create(name="Двигатель", scope="auto")
    with pytest.raises(Exception):  # IntegrityError
        Category.objects.create(name="Двигатель", scope="auto")


@pytest.mark.django_db
def test_category_str():
    c = Category.objects.create(name="Двигатель", scope="auto")
    assert "Двигатель" in str(c)
    assert "Авто" in str(c)


# ---------- Wheel.clean(): tire ----------

@pytest.mark.django_db
def test_wheel_tire_requires_tire_fields():
    w = Wheel(product_form="tire", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car")
    with pytest.raises(ValidationError) as exc:
        w.clean()
    for f in ("tire_width", "tire_profile", "tire_diameter", "season"):
        assert f in exc.value.message_dict


@pytest.mark.django_db
def test_wheel_tire_ok():
    w = Wheel(product_form="tire", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer")
    w.clean()  # не падает


@pytest.mark.django_db
def test_wheel_tire_used_requires_tread():
    w = Wheel(product_form="tire", condition="used", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer")
    with pytest.raises(ValidationError) as exc:
        w.clean()
    assert "tread_remain" in exc.value.message_dict


# ---------- Wheel.clean(): rim ----------

@pytest.mark.django_db
def test_wheel_rim_requires_rim_fields():
    w = Wheel(product_form="rim", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car")
    with pytest.raises(ValidationError) as exc:
        w.clean()
    for f in ("rim_diameter", "rim_type", "pcd_bolt_count",
              "pcd_diameter", "offset_et"):
        assert f in exc.value.message_dict


@pytest.mark.django_db
def test_wheel_rim_ok():
    w = Wheel(product_form="rim", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car",
              rim_diameter=17, rim_type="alloy", pcd_bolt_count=5,
              pcd_diameter=Decimal("114.3"), offset_et=45)
    w.clean()


# ---------- Wheel.clean(): set ----------

@pytest.mark.django_db
def test_wheel_set_requires_both():
    w = Wheel(product_form="set", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer")
    with pytest.raises(ValidationError) as exc:
        w.clean()
    # не хватает rim-полей
    for f in ("rim_diameter", "rim_type", "pcd_bolt_count",
              "pcd_diameter", "offset_et"):
        assert f in exc.value.message_dict


@pytest.mark.django_db
def test_wheel_set_ok():
    w = Wheel(product_form="set", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer",
              rim_diameter=17, rim_type="alloy", pcd_bolt_count=5,
              pcd_diameter=Decimal("114.3"), offset_et=45)
    w.clean()


# ---------- Factories ----------

@pytest.mark.django_db
def test_factory_auto_part():
    p = AutoPartFactory()
    assert p.pk
    assert p.category.scope == "auto"


@pytest.mark.django_db
def test_factory_moto_part():
    p = MotoPartFactory()
    assert p.pk
    assert p.category.scope == "moto"


@pytest.mark.django_db
def test_factory_wheel():
    w = WheelFactory()
    assert w.pk
    assert w.product_form == "tire"

# ---------- Wheel.clean(): дополнительные ветки ----------

@pytest.mark.django_db
def test_wheel_tire_used_ok_with_tread():
    """Б/у шина с остатком протектора — валидна."""
    w = Wheel(product_form="tire", condition="used", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer",
              tread_remain=Decimal("4.0"))
    w.clean()  # не падает


@pytest.mark.django_db
def test_wheel_set_used_requires_tread():
    """Б/у комплект без протектора — ошибка на tread_remain."""
    w = Wheel(product_form="set", condition="used", name="t",
              price=Decimal("100"), vehicle_kind="car",
              tire_width=205, tire_profile=55, tire_diameter=16, season="summer",
              rim_diameter=17, rim_type="alloy", pcd_bolt_count=5,
              pcd_diameter=Decimal("114.3"), offset_et=45)
    with pytest.raises(ValidationError) as exc:
        w.clean()
    assert "tread_remain" in exc.value.message_dict


@pytest.mark.django_db
def test_wheel_clean_unknown_product_form_ok():
    """Неизвестный product_form — clean() не падает (нет required)."""
    w = Wheel(product_form="unknown", condition="new", name="t",
              price=Decimal("100"), vehicle_kind="car")
    w.clean()  # не падает, required пустой    