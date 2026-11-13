import pytest
from django.urls import reverse

from apps.catalog.tests.factories import (
    AutoPartFactory, MotoPartFactory, WheelFactory,
)


# ---------- index ----------

@pytest.mark.django_db
def test_index_ok(client):
    AutoPartFactory(name="Авто-деталь")
    MotoPartFactory(name="Мото-деталь")
    WheelFactory(name="Колесо")
    r = client.get(reverse("index"))
    assert r.status_code == 200
    assert "Авто-деталь" in r.content.decode()
    assert "Мото-деталь" in r.content.decode()
    assert "Колесо" in r.content.decode()


@pytest.mark.django_db
def test_index_only_active(client):
    AutoPartFactory(name="Активная", is_active=True)
    AutoPartFactory(name="Неактивная", is_active=False)
    r = client.get(reverse("index"))
    assert r.status_code == 200
    assert "Активная" in r.content.decode()
    assert "Неактивная" not in r.content.decode()


@pytest.mark.django_db
def test_index_empty(client):
    r = client.get(reverse("index"))
    assert r.status_code == 200


# ---------- product_detail ----------

@pytest.mark.django_db
def test_product_detail_wheel_ok(client):
    w = WheelFactory(name="Шина X")
    r = client.get(reverse("product_detail", args=["wheel", w.pk]))
    assert r.status_code == 200
    assert "Шина X" in r.content.decode()


@pytest.mark.django_db
def test_product_detail_auto_ok(client):
    p = AutoPartFactory(name="Деталь Y")
    r = client.get(reverse("product_detail", args=["auto", p.pk]))
    assert r.status_code == 200
    assert "Деталь Y" in r.content.decode()


@pytest.mark.django_db
def test_product_detail_moto_ok(client):
    p = MotoPartFactory(name="Деталь Z")
    r = client.get(reverse("product_detail", args=["moto", p.pk]))
    assert r.status_code == 200
    assert "Деталь Z" in r.content.decode()


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
def test_product_detail_wrong_kind_404(client):
    """kind не из MODELS — сейчас KeyError (500), а не 404.

    Это баг: MODELS[kind] без .get(). Тест фиксирует текущее поведение.
    Если починим вьюху — поменять на 404.
    """
    w = WheelFactory()
    with pytest.raises(KeyError):
        client.get(reverse("product_detail", args=["unknown", w.pk]))