
import factory
from decimal import Decimal

from apps.catalog.models import (
    Category, CarModel, MotoModel, AutoPart, MotoPart, Wheel,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name", "scope")

    name = factory.Sequence(lambda n: f"Категория {n}")
    scope = "auto"


class CarModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarModel

    make = "Toyota"
    model = factory.Sequence(lambda n: f"Model{n}")
    generation = ""


class MotoModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MotoModel

    make = "Yamaha"
    model = factory.Sequence(lambda n: f"Moto{n}")


class AutoPartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AutoPart

    name = factory.Sequence(lambda n: f"Автозапчасть {n}")
    category = factory.SubFactory(CategoryFactory, scope="auto")
    part_type = "Двигатель"
    condition = "new"
    price = Decimal("1000.00")
    stock = 1
    is_active = True


class MotoPartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MotoPart

    name = factory.Sequence(lambda n: f"Мотозапчасть {n}")
    category = factory.SubFactory(CategoryFactory, scope="moto")
    part_type = "Двигатель"
    condition = "new"
    price = Decimal("2000.00")
    stock = 1
    is_active = True


class WheelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wheel

    name = factory.Sequence(lambda n: f"Колесо {n}")
    vehicle_kind = "car"
    product_form = "tire"
    condition = "new"
    price = Decimal("5000.00")
    stock = 1
    is_active = True
    tire_width = 205
    tire_profile = 55
    tire_diameter = 16
    season = "summer"