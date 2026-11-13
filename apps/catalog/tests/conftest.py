import pytest
from django.core.management import call_command


@pytest.fixture
def categories(db):
    """22 категории: 13 auto + 9 moto (из dicts)."""
    from apps.catalog.models import Category
    from apps.catalog.dicts import PART_TYPES_AUTO, PART_TYPES_MOTO
    for n in PART_TYPES_AUTO:
        Category.objects.get_or_create(name=n, scope="auto")
    for n in PART_TYPES_MOTO:
        Category.objects.get_or_create(name=n, scope="moto")
    return Category.objects.all()


@pytest.fixture
def car_model(db):
    from apps.catalog.models import CarModel
    return CarModel.objects.create(make="Toyota", model="Camry", generation="XV70")


@pytest.fixture
def moto_model(db):
    from apps.catalog.models import MotoModel
    return MotoModel.objects.create(make="Yamaha", model="YZF-R1")