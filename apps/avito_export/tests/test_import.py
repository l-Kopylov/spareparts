# apps/avito_export/tests/test_import.py

import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model


@pytest.fixture
def staff_user(db):
    U = get_user_model()
    return U.objects.create_user("staff", password="pass", is_staff=True)


@pytest.mark.django_db
def test_import_post_ok(client, staff_user):
    xml = b'<?xml version="1.0"?><Ads formatVersion="3" target="Avito.ru"><Ad><Id>wheel-x</Id><Title>T</Title><Description>D</Description><Price>100</Price><Category>C</Category><Address>A</Address></Ad></Ads>'
    f = SimpleUploadedFile("test.xml", xml, content_type="application/xml")
    client.force_login(staff_user)
    r = client.post(reverse("avito_import"), {"file": f, "batch_name": "Тест"})
    assert r.status_code == 200
    assert r.context["result"].created == 1
