import pytest
from decimal import Decimal
from django import forms

from apps.catalog.forms import WheelForm, AutoPartForm, MotoPartForm
from apps.catalog.tests.factories import CategoryFactory


# ---------- WheelForm: видимость ----------

@pytest.mark.django_db
def test_wheel_form_tire_hides_rim():
    f = WheelForm(data={"product_form": "tire"})
    for name in ("rim_width", "rim_diameter", "rim_type",
                 "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore"):
        assert isinstance(f.fields[name].widget, forms.HiddenInput), name


@pytest.mark.django_db
def test_wheel_form_rim_hides_tire():
    f = WheelForm(data={"product_form": "rim"})
    for name in ("tire_width", "tire_profile", "tire_diameter",
                 "season", "tread_remain"):
        assert isinstance(f.fields[name].widget, forms.HiddenInput), name


@pytest.mark.django_db
def test_wheel_form_set_shows_all():
    f = WheelForm(data={"product_form": "set"})
    for name in ("tire_width", "rim_diameter", "pcd_bolt_count"):
        assert not isinstance(f.fields[name].widget, forms.HiddenInput), name


# ---------- WheelForm: required ----------

@pytest.mark.django_db
def test_wheel_form_tire_required():
    f = WheelForm(data={"product_form": "tire"})
    assert f.fields["tire_width"].required is True
    assert f.fields["rim_diameter"].required is False


# ---------- WheelForm: choices из словарей ----------

@pytest.mark.django_db
def test_wheel_form_car_choices():
    f = WheelForm(initial={"vehicle_kind": "car"})
    values = [v for v, _ in f.fields["tire_width"].choices]
    assert "205" in values


@pytest.mark.django_db
def test_wheel_form_moto_choices():
    f = WheelForm(initial={"vehicle_kind": "moto"})
    values = [v for v, _ in f.fields["tire_width"].choices]
    assert "205" not in values


# ---------- WheelForm: clean() ----------

@pytest.mark.django_db
def test_wheel_form_clean_hides_rim_to_empty_string():
    data = {
        "name": "t", "description": "", "price": "100", "stock": "1",
        "condition": "new", "brand": "", "oem": "", "is_active": "on",
        "vehicle_kind": "car", "product_form": "tire", "model_name": "",
        "tire_width": "205", "tire_profile": "55", "tire_diameter": "16",
        "season": "summer", "tread_remain": "", "items_count": "4",
        "rim_width": "", "rim_diameter": "", "rim_type": "",
        "pcd_bolt_count": "", "pcd_diameter": "", "offset_et": "", "center_bore": "",
    }
    f = WheelForm(data=data)
    assert f.is_valid(), f.errors
    assert f.cleaned_data["rim_type"] == ""
    assert f.cleaned_data["rim_width"] is None
    assert f.cleaned_data["tire_width"] == 205
    assert f.cleaned_data["season"] == "summer"


# ---------- AutoPartForm / MotoPartForm ----------

@pytest.mark.django_db
def test_auto_form_filters_auto_categories():
    CategoryFactory(name="Двигатель", scope="auto")
    CategoryFactory(name="Двигатель", scope="moto")
    f = AutoPartForm()
    scopes = set(f.fields["category"].queryset.values_list("scope", flat=True))
    assert scopes == {"auto"}


@pytest.mark.django_db
def test_moto_form_filters_moto_categories():
    CategoryFactory(name="Двигатель", scope="auto")
    CategoryFactory(name="Двигатель", scope="moto")
    f = MotoPartForm()
    scopes = set(f.fields["category"].queryset.values_list("scope", flat=True))
    assert scopes == {"moto"}


@pytest.mark.django_db
def test_auto_form_part_type_choices():
    f = AutoPartForm()
    assert len(f.fields["part_type"].choices) == 13


@pytest.mark.django_db
def test_moto_form_part_type_choices():
    f = MotoPartForm()
    assert len(f.fields["part_type"].choices) == 9

@pytest.mark.django_db
def test_wheel_form_rim_required():
    f = WheelForm(data={"product_form": "rim"})
    assert f.fields["rim_diameter"].required is True
    assert f.fields["tire_width"].required is False

@pytest.mark.django_db
def test_wheel_form_set_required():
    f = WheelForm(data={"product_form": "set"})
    assert f.fields["tire_width"].required is True
    assert f.fields["rim_diameter"].required is True   

@pytest.mark.django_db
def test_wheel_form_clean_hides_tire():
    data = {
        "name": "t", "description": "", "price": "100", "stock": "1",
        "condition": "new", "brand": "", "oem": "", "is_active": "on",
        "vehicle_kind": "car", "product_form": "rim", "model_name": "",
        "tire_width": "", "tire_profile": "", "tire_diameter": "",
        "season": "", "tread_remain": "", "items_count": "4",
        "rim_width": "7", "rim_diameter": "17", "rim_type": "alloy",
        "pcd_bolt_count": "5", "pcd_diameter": "114.3", "offset_et": "45",
        "center_bore": "60.1",
    }
    f = WheelForm(data=data)
    assert f.is_valid(), f.errors
    assert f.cleaned_data["tire_width"] is None
    assert f.cleaned_data["season"] == ""
    assert f.cleaned_data["rim_diameter"] == 17        

@pytest.mark.django_db
def test_wheel_form_clean_set_keeps_all():
    data = {
        "name": "t", "description": "", "price": "100", "stock": "1",
        "condition": "new", "brand": "", "oem": "", "is_active": "on",
        "vehicle_kind": "car", "product_form": "set", "model_name": "",
        "tire_width": "205", "tire_profile": "55", "tire_diameter": "16",
        "season": "summer", "tread_remain": "", "items_count": "4",
        "rim_width": "7", "rim_diameter": "17", "rim_type": "alloy",
        "pcd_bolt_count": "5", "pcd_diameter": "114.3", "offset_et": "45",
        "center_bore": "60.1",
    }
    f = WheelForm(data=data)
    assert f.is_valid(), f.errors
    assert f.cleaned_data["tire_width"] == 205
    assert f.cleaned_data["rim_diameter"] == 17
    assert f.cleaned_data["season"] == "summer"   

@pytest.mark.django_db
def test_auto_form_saves():
    cat = CategoryFactory(name="Двигатель", scope="auto")
    f = AutoPartForm(data={
        "name": "Двигатель", "category": cat.pk, "part_type": "Двигатель",
        "condition": "new", "price": "1000", "stock": "1", "is_active": "on",
        "description": "",
    })
    assert f.is_valid(), f.errors
    obj = f.save()
    assert obj.pk
    assert obj.category.scope == "auto"   
@pytest.mark.django_db
def test_moto_form_saves():
    cat = CategoryFactory(name="Двигатель", scope="moto")
    f = MotoPartForm(data={
        "name": "Двигатель", "category": cat.pk, "part_type": "Двигатель",
        "condition": "new", "price": "2000", "stock": "1", "is_active": "on",
        "description": "",
    })
    assert f.is_valid(), f.errors
    obj = f.save()
    assert obj.pk
    assert obj.category.scope == "moto" 

@pytest.mark.django_db
def test_wheel_form_car_rim_diameters():
    f = WheelForm(initial={"vehicle_kind": "car"})
    values = [v for v, _ in f.fields["rim_diameter"].choices]
    assert "17" in values


@pytest.mark.django_db
def test_wheel_form_moto_rim_diameters():
    f = WheelForm(initial={"vehicle_kind": "moto"})
    values = [v for v, _ in f.fields["rim_diameter"].choices]
    assert "17" in values  # 17 есть и у мото