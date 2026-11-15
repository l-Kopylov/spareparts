# apps/avito_export/services/avito_xml.py
"""Экспорт/импорт XML по формату автозагрузки Авито (Ads/Ad).

Формат: https://autoload.avito.ru/format
Корень: <Ads formatVersion="3" target="Avito.ru">
Внутри: <Ad>...</Ad> для каждого объявления.

Экспорт: поддерживает Wheel, AutoPart, MotoPart (через MAPPER_BY_MODEL).
Импорт: пока только Wheel (импорт авто/мото — отдельным шагом).
"""
import xml.etree.ElementTree as ET
from decimal import Decimal

from .base import BaseExporter, BaseImporter
from .schemas import FeedItem, ImportResult
from .mapping import WheelMapper, AutoPartMapper, MotoPartMapper
from apps.catalog.models import Wheel, AutoPart, MotoPart


# Какой маппер использовать для какого типа модели
MAPPER_BY_MODEL = {
    Wheel: WheelMapper,
    AutoPart: AutoPartMapper,
    MotoPart: MotoPartMapper,
}

# после MAPPER_BY_MODEL
IMPORTER_BY_KIND = {
    "wheel": (Wheel, WheelMapper),
    "auto": (AutoPart, AutoPartMapper),
    "moto": (MotoPart, MotoPartMapper),
}


class AvitoXmlExporter(BaseExporter):
    """Экспорт списка моделей (Wheel/AutoPart/MotoPart) в XML-фид Авито."""

    def export(self, items) -> bytes:
        """Собрать XML (bytes) из списка моделей.

        items — список объектов (Wheel/AutoPart/MotoPart).
        Маппер выбирается по типу объекта (MAPPER_BY_MODEL).
        """
        root = ET.Element("Ads", {
            "formatVersion": "3",
            "target": "Avito.ru",
        })

        for obj in items:
            mapper = MAPPER_BY_MODEL.get(type(obj))
            if mapper is None:
                continue  # неизвестный тип — пропускаем
            item = mapper.to_feed_item(obj)

            ad = ET.SubElement(root, "Ad")
            ET.SubElement(ad, "Id").text = item.external_id
            ET.SubElement(ad, "Title").text = item.title
            ET.SubElement(ad, "Description").text = item.description
            ET.SubElement(ad, "Price").text = str(int(item.price))
            ET.SubElement(ad, "Category").text = item.category
            ET.SubElement(ad, "Address").text = item.address
            ET.SubElement(ad, "Condition").text = item.condition

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)


class AvitoXmlImporter(BaseImporter):
    """Импорт XML-фида Авито в FeedItem'ы и запись в БД (пока только Wheel)."""

    def parse(self, file) -> list[FeedItem]:
        """Разобрать XML в список FeedItem."""
        tree = ET.parse(file)
        root = tree.getroot()
        items: list[FeedItem] = []

        for ad in root.findall("Ad"):
            items.append(FeedItem(
                external_id=ad.findtext("Id", ""),
                title=ad.findtext("Title", ""),
                description=ad.findtext("Description", ""),
                price=Decimal(ad.findtext("Price", "0")),
                category=ad.findtext("Category", ""),
                address=ad.findtext("Address", ""),
                condition=ad.findtext("Condition", "Новое"),
            ))
        return items

    def import_to_db(self, items: list[FeedItem], batch_name: str = "",
                     kind: str = "wheel") -> ImportResult:
        """Записать FeedItem'ы в БД (model/mapper по kind). upsert по external_id."""
        from django.db import transaction
        from ..validators import validate_feed_item

        if kind not in IMPORTER_BY_KIND:
            raise ValueError(f"Неизвестный kind: {kind}")
        model, mapper = IMPORTER_BY_KIND[kind]

        result = ImportResult(total=len(items))

        try:
            with transaction.atomic():
                for i, item in enumerate(items, start=1):
                    errs = validate_feed_item(item, kind=kind)
                    if errs:
                        result.skipped += 1
                        result.errors.append({
                            "row": i,
                            "external_id": item.external_id,
                            "message": "; ".join(errs),
                        })
                        continue

                    try:
                        with transaction.atomic():
                            data = mapper.from_feed_item(item, batch_name=batch_name)
                            _, created = model.objects.update_or_create(
                                external_id=item.external_id,
                                defaults=data,
                            )
                        if created:
                            result.created += 1
                        else:
                            result.updated += 1
                    except Exception as e:
                        result.skipped += 1
                        result.errors.append({
                            "row": i,
                            "external_id": item.external_id,
                            "message": f"Ошибка БД: {e}",
                        })
        except Exception as e:
            result.errors.append({"row": "ALL", "message": f"Транзакция откатилась: {e}"})
            raise

        return result