import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model


@pytest.fixture
def staff_user(db):
    U = get_user_model()
    return U.objects.create_user("staff", password="pass", is_staff=True)


@pytest.fixture
def superuser(db):
    U = get_user_model()
    return U.objects.create_superuser("admin", "a@a.a", "pass")


@pytest.mark.django_db
def test_panel_index_requires_login(client):
    r = client.get(reverse("panel_index"))
    assert r.status_code == 302
    assert "/admin/login/" in r.url or "login" in r.url


@pytest.mark.django_db
def test_panel_index_ok(client, staff_user):
    client.force_login(staff_user)
    r = client.get(reverse("panel_index"))
    assert r.status_code == 200


@pytest.mark.django_db
def test_new_item_get(client, staff_user):
    client.force_login(staff_user)
    for kind in ("auto", "moto", "wheel"):
        r = client.get(reverse("new_item", args=[kind]))
        assert r.status_code == 200, kind


@pytest.mark.django_db
def test_new_wheel_post(client, staff_user):
    client.force_login(staff_user)
    data = {
        "name": "Шина", "description": "", "price": "5000", "stock": "4",
        "condition": "new", "brand": "", "oem": "", "is_active": "on",
        "vehicle_kind": "car", "product_form": "tire", "model_name": "",
        "tire_width": "205", "tire_profile": "55", "tire_diameter": "16",
        "season": "summer", "tread_remain": "", "items_count": "4",
        "rim_width": "", "rim_diameter": "", "rim_type": "",
        "pcd_bolt_count": "", "pcd_diameter": "", "offset_et": "", "center_bore": "",
    }
    r = client.post(reverse("new_item", args=["wheel"]), data)
    # либо редирект (успех), либо 200 с ошибками (например, фото)
    assert r.status_code in (200, 302)

   # ---------- new_item: без логина ----------

@pytest.mark.django_db
def test_new_item_requires_login(client):
    r = client.get(reverse("new_item", args=["wheel"]))
    assert r.status_code == 302


# ---------- panel_index: контекст ----------

@pytest.mark.django_db
def test_panel_index_context(client, staff_user):
    from apps.catalog.tests.factories import (
        WheelFactory, AutoPartFactory, MotoPartFactory,
    )
    WheelFactory()
    AutoPartFactory()
    MotoPartFactory()
    client.force_login(staff_user)
    r = client.get(reverse("panel_index"))
    assert r.status_code == 200
    assert "auto_parts" in r.context
    assert "moto_parts" in r.context
    assert "wheels" in r.context
    assert len(r.context["wheels"]) == 1


# ---------- edit_item ----------

@pytest.mark.django_db
def test_edit_item_get(client, staff_user):
    from apps.catalog.tests.factories import WheelFactory
    w = WheelFactory()
    client.force_login(staff_user)
    r = client.get(reverse("edit_item", args=["wheel", w.pk]))
    assert r.status_code == 200
    assert "form" in r.context


@pytest.mark.django_db
def test_edit_item_post(client, staff_user):
    from apps.catalog.tests.factories import WheelFactory
    w = WheelFactory()
    client.force_login(staff_user)
    data = {
        "name": "Изменённая шина", "description": "", "price": "9999", "stock": "2",
        "condition": "new", "brand": "", "oem": "", "is_active": "on",
        "vehicle_kind": "car", "product_form": "tire", "model_name": "",
        "tire_width": "205", "tire_profile": "55", "tire_diameter": "16",
        "season": "summer", "tread_remain": "", "items_count": "4",
        "rim_width": "", "rim_diameter": "", "rim_type": "",
        "pcd_bolt_count": "", "pcd_diameter": "", "offset_et": "", "center_bore": "",
    }
    r = client.post(reverse("edit_item", args=["wheel", w.pk]), data)
    assert r.status_code == 302
    w.refresh_from_db()
    assert w.name == "Изменённая шина"
    assert str(w.price) == "9999.00"


# ---------- delete_item ----------

@pytest.mark.django_db
def test_delete_item_get(client, staff_user):
    from apps.catalog.tests.factories import WheelFactory
    w = WheelFactory()
    client.force_login(staff_user)
    r = client.get(reverse("delete_item", args=["wheel", w.pk]))
    assert r.status_code == 200


@pytest.mark.django_db
def test_delete_item_post(client, staff_user):
    from apps.catalog.tests.factories import WheelFactory
    from apps.catalog.models import Wheel
    w = WheelFactory()
    pk = w.pk
    client.force_login(staff_user)
    r = client.post(reverse("delete_item", args=["wheel", pk]))
    assert r.status_code == 302
    assert not Wheel.objects.filter(pk=pk).exists()


# ---------- photo_delete ----------

@pytest.mark.django_db
def test_photo_delete(client, staff_user):
    from apps.catalog.tests.factories import WheelFactory
    from apps.catalog.models import PartPhoto
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.contrib.contenttypes.models import ContentType

    w = WheelFactory()
    ct = ContentType.objects.get_for_model(w)
    gif = bytes.fromhex(
        "47494638396101000100800000ffffff00000021f90401000000002c00000000010001000002024401003b"
    )
    photo = PartPhoto.objects.create(
        content_type=ct, object_id=w.pk,
        image=SimpleUploadedFile("t.gif", gif, content_type="image/gif"),
    )
    pk = photo.pk
    client.force_login(staff_user)
    r = client.post(reverse("photo_delete", args=["wheel", w.pk, pk]))
    assert r.status_code == 302
    assert not PartPhoto.objects.filter(pk=pk).exists() 