# apps/avito_export/services/mapping.py
"""Маппинг: модель Django <-> FeedItem.

Каждый маппер знает два направления:
  to_feed_item(model) -> FeedItem      (для экспорта)
  from_feed_item(item, batch) -> dict  (для импорта, dict для update_or_create)
"""
from apps.catalog.models import Wheel, AutoPart, MotoPart, Category
from .schemas import FeedItem


class WheelMapper:
    """Маппер для колёс/шин/дисков (Wheel)."""

    @staticmethod
    def to_feed_item(wheel: Wheel) -> FeedItem:
        """Wheel -> FeedItem (для экспорта)."""
        ext_id = wheel.external_id or f"wheel-{wheel.pk}"
        return FeedItem(
            external_id=ext_id,
            title=wheel.name[:50],
            description=(wheel.description or wheel.name)[:3000],
            price=wheel.price,
            category="Колёса и шины",
            address="Москва",
            condition="Новое" if wheel.condition == "new" else "Б/у",
            tire_width=wheel.tire_width,
            tire_profile=wheel.tire_profile,
            tire_diameter=wheel.tire_diameter,
            rim_diameter=wheel.rim_diameter,
            rim_type=wheel.get_rim_type_display() if wheel.rim_type else None,
            pcd_bolt_count=wheel.pcd_bolt_count,
            pcd_diameter=wheel.pcd_diameter,
            offset_et=wheel.offset_et,
        )

    @staticmethod
    def from_feed_item(item: FeedItem, batch_name: str = "") -> dict:
        """FeedItem -> dict для Wheel.objects.update_or_create()."""
        return {
            "external_id": item.external_id,
            "batch_name": batch_name,
            "name": item.title,
            "description": item.description,
            "price": item.price,
            "condition": "new" if item.condition == "Новое" else "used",
            # обязательные поля Wheel (null=False, без default)
            "vehicle_kind": "car",      # дефолт: авто (можно уточнить из item)
            "product_form": "tire",     # дефолт: шина (можно уточнить)
            "season": "",               # CharField(blank=True), но null=False → ""
            "rim_type": item.rim_type or "",
            # размеры (null=True, можно None)
            "tire_width": item.tire_width,
            "tire_profile": item.tire_profile,
            "tire_diameter": item.tire_diameter,
            "rim_diameter": item.rim_diameter,
            "pcd_bolt_count": item.pcd_bolt_count,
            "pcd_diameter": item.pcd_diameter,
            "offset_et": item.offset_et,
        }


class AutoPartMapper:
    """Маппер для авто-деталей (AutoPart)."""

    @staticmethod
    def to_feed_item(part: AutoPart) -> FeedItem:
        """AutoPart -> FeedItem (для экспорта)."""
        ext_id = part.external_id or f"auto-{part.pk}"
        return FeedItem(
            external_id=ext_id,
            title=part.name[:50],
            description=(part.description or part.name)[:3000],
            price=part.price,
            category=part.part_type or "Запчасти",
            address="Москва",
            condition="Новое" if part.condition == "new" else "Б/у",
        )

    @staticmethod
    def from_feed_item(item: FeedItem, batch_name: str = "") -> dict:
        """FeedItem -> dict для AutoPart.objects.update_or_create()."""
        cat = Category.objects.filter(name=item.category, scope="auto").first()
        return {
            "external_id": item.external_id,
            "batch_name": batch_name,
            "name": item.title,
            "description": item.description,
            "price": item.price,
            "condition": "new" if item.condition == "Новое" else "used",
            "part_type": item.category,
            "category": cat,   # FK (None, если не нашли — валидатор отсеет)
        }


class MotoPartMapper:
    """Маппер для мото-деталей (MotoPart)."""

    @staticmethod
    def to_feed_item(part: MotoPart) -> FeedItem:
        """MotoPart -> FeedItem (для экспорта)."""
        ext_id = part.external_id or f"moto-{part.pk}"
        return FeedItem(
            external_id=ext_id,
            title=part.name[:50],
            description=(part.description or part.name)[:3000],
            price=part.price,
            category=part.part_type or "Запчасти",
            address="Москва",
            condition="Новое" if part.condition == "new" else "Б/у",
        )

    @staticmethod
    def from_feed_item(item: FeedItem, batch_name: str = "") -> dict:
        """FeedItem -> dict для MotoPart.objects.update_or_create()."""
        cat = Category.objects.filter(name=item.category, scope="moto").first()
        return {
            "external_id": item.external_id,
            "batch_name": batch_name,
            "name": item.title,
            "description": item.description,
            "price": item.price,
            "condition": "new" if item.condition == "Новое" else "used",
            "part_type": item.category,
            "category": cat,   # FK (None, если не нашли — валидатор отсеет)
        }
