import pytest
from django.urls import reverse

from apps.catalog.tests.factories import (
    AutoPartFactory, MotoPartFactory, WheelFactory,
)


# ---------- index: по умолчанию auto ----------

@pytest.mark.django_db
def test_index_default_auto(client):
    AutoPartFactory(name="Авто-деталь")
    MotoPartFactory(name="Мото-деталь")
    WheelFactory(name="Колесо")
    r = client.get(reverse("index"))
    assert r.status_code == 200
    assert r.context["kind"] == "auto"
    names = [p.name for p in r.context["items"]]
    assert "Авто-деталь" in names
    assert "Мото-деталь" not in names
    assert "Колесо" not in names


@pytest.mark.django_db
def test_index_moto(client):
    MotoPartFactory(name="Мото-деталь")
    r = client.get(reverse("index") + "?kind=moto")
    assert r.status_code == 200
    assert r.context["kind"] == "moto"
    names = [p.name for p in r.context["items"]]
    assert "Мото-деталь" in names


@pytest.mark.django_db
def test_index_wheel(client):
    WheelFactory(name="Колесо")
    r = client.get(reverse("index") + "?kind=wheel")
    assert r.status_code == 200
    assert r.context["kind"] == "wheel"
    names = [p.name for p in r.context["items"]]
    assert "Колесо" in names


@pytest.mark.django_db
def test_index_unknown_kind_falls_back_to_auto(client):
    r = client.get(reverse("index") + "?kind=unknown")
    assert r.status_code == 200
    assert r.context["kind"] == "auto"


@pytest.mark.django_db
def test_index_only_active(client):
    AutoPartFactory(name="Активная", is_active=True)
    AutoPartFactory(name="Неактивная", is_active=False)
    r = client.get(reverse("index"))
    names = [p.name for p in r.context["items"]]
    assert "Активная" in names
    assert "Неактивная" not in names


@pytest.mark.django_db
def test_index_empty(client):
    r = client.get(reverse("index"))
    assert r.status_code == 200
    assert list(r.context["items"]) == []


# ---------- product_detail ----------

@pytest.mark.django_db
def test_product_detail_wheel_ok(client):
    w = WheelFactory(name="Шина X")
    r = client.get(reverse("product_detail", args=["wheel", w.pk]))
    assert r.status_code == 200
    assert r.context["item"].name == "Шина X"


@pytest.mark.django_db
def test_product_detail_auto_ok(client):
    p = AutoPartFactory(name="Деталь Y")
    r = client.get(reverse("product_detail", args=["auto", p.pk]))
    assert r.status_code == 200
    assert r.context["item"].name == "Деталь Y"


@pytest.mark.django_db
def test_product_detail_moto_ok(client):
    p = MotoPartFactory(name="Деталь Z")
    r = client.get(reverse("product_detail", args=["moto", p.pk]))
    assert r.status_code == 200
    assert r.context["item"].name == "Деталь Z"


@pytest.mark.django_db
def test_product_detail_404(client):
    r = client.get(reverse("product_detail", args=["wheel", 999999]))
    assert r.status_code == 404


@pytest.mark.django_db
def test_product_detail_inactive_404(client):
    w = WheelFactory(name="Неактивная", is_active=False)
    r = client.get(reverse("product_detail", args=["wheel", w.pk]))
    assert r.status_code == 404


@pytest.mark.django_db
def test_product_detail_unknown_kind_404(client):
    """kind не из MODELS — теперь 404 (починили views.py)."""
    w = WheelFactory()
    r = client.get(reverse("product_detail", args=["unknown", w.pk]))
    assert r.status_code == 404