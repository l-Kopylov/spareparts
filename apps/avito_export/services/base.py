
# apps/avito_export/services/base.py
"""Абстрактные базовые классы для экспортёров/импортёров.

Паттерн Strategy: вьюха не знает, XML это или JSON. Она вызывает
exporter.export(qs) / importer.parse(file), а конкретный класс
решает, как это сделать.

ABC (Abstract Base Class) — «должностная инструкция»:
если класс наследует BaseExporter, но не реализует export(),
Python не даст создать его экземпляр (TypeError).
"""
from abc import ABC, abstractmethod

from .schemas import FeedItem


class BaseExporter(ABC):
    """Контракт экспортёра: queryset -> bytes (содержимое файла)."""

    @abstractmethod
    def export(self, queryset) -> bytes:
        """Собрать файл (bytes) из queryset моделей.

        Args:
            queryset: QuerySet (Wheel / AutoPart / MotoPart).

        Returns:
            bytes — содержимое файла (XML/JSON), готовое к скачиванию.
        """
        ...


class BaseImporter(ABC):
    """Контракт импортёра: file -> list[FeedItem]."""

    @abstractmethod
    def parse(self, file) -> list[FeedItem]:
        """Разобрать файл в список FeedItem.

        Args:
            file: файловый объект (request.FILES["file"]) или путь.

        Returns:
            list[FeedItem] — строки фида (без записи в БД).
        """
        ...

    @abstractmethod
    def import_to_db(self, items: list[FeedItem], batch_name: str = ""):
        """Записать FeedItem'ы в БД. Вернуть ImportResult.

        Args:
            items: список FeedItem (после валидации).
            batch_name: «серия засева» (ИП Пупкин, ООО Рога и Копыта 2).

        Returns:
            ImportResult — отчёт (created/updated/skipped/errors).
        """
        ...
