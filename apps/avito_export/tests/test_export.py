# apps/avito_export/tests/test_export.py

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.catalog.tests.factories import WheelFactory, AutoPartFactory, MotoPartFactory


@pytest.fixture
def staff_user(db):
    U = get_user_model()
    return U.objects.create_user("staff", password="pass", is_staff=True)


@pytest.mark.django_db
def test_export_requires_login(client):
    r = client.get(reverse("avito_export", args=["wheel"]))
    assert r.status_code == 302


@pytest.mark.django_db
def test_export_wheel_only(client, staff_user):
    WheelFactory(name="Шина X")
    AutoPartFactory(name="Деталь Y")
    client.force_login(staff_user)
    r = client.get(reverse("avito_export", args=["wheel"]))
    assert r.status_code == 200
    assert b"<Id>wheel-" in r.content
    assert b"auto-" not in r.content


@pytest.mark.django_db
def test_export_auto_only(client, staff_user):
    WheelFactory(name="Шина X")
    AutoPartFactory(name="Деталь Y")
    client.force_login(staff_user)
    r = client.get(reverse("avito_export", args=["auto"]))
    assert r.status_code == 200
    assert b"<Id>auto-" in r.content
    assert b"wheel-" not in r.content


@pytest.mark.django_db
def test_export_page(client, staff_user):
    client.force_login(staff_user)
    r = client.get(reverse("avito_export_page"))
    assert r.status_code == 200
    assert "kinds" in r.context
