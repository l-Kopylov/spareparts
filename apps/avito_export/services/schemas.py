# apps/avito_export/services/schemas.py
"""DTO (Data Transfer Object) — «конверты» для данных.

FeedItem — одна строка фида (одно объявление), независимо от формата (XML/JSON).
ImportResult — отчёт об импорте (сколько создано/обновлено/ошибок).

Зачем dataclass, а не dict:
- IDE подсказывает поля (не опечатаешься в ключе);
- типы видны (price: Decimal, а не «строка или число»);
- легко тестировать (сравниваешь два FeedItem).
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class FeedItem:
    """Одна строка фида — одно объявление.

    Обязательные поля (Авито требует):
      Id, Title, Description, Price, Category, Address.

    Опциональные:
      AvitoId (если объявление уже на Авито), Condition, Photos,
      ManagerName, ContactPhone, специфичные для колёс.
    """
    # --- обязательные ---
    external_id: str                    # Id (наш стабильный идентификатор: wheel-1, auto-5)
    title: str                          # Title (до 50 символов)
    description: str                    # Description (до 3000 символов)
    price: Decimal                      # Price (целое, руб.)
    category: str                       # Category (по классификатору Авито)
    address: str                        # Address (город обязателен)

    # --- опциональные (общие) ---
    avito_id: Optional[str] = None      # AvitoId (если объявление уже на Авито)
    condition: str = "Новое"            # Condition (Новое/Б/у)
    photos: list[str] = field(default_factory=list)  # Photo url (https)
    manager_name: str = ""              # ManagerName (контактное лицо)
    contact_phone: str = ""             # ContactPhone

    # --- специфичные для колёс (опционально) ---
    tire_width: Optional[int] = None
    tire_profile: Optional[int] = None
    tire_diameter: Optional[int] = None
    rim_diameter: Optional[int] = None
    rim_type: Optional[str] = None
    pcd_bolt_count: Optional[int] = None
    pcd_diameter: Optional[Decimal] = None
    offset_et: Optional[int] = None


@dataclass
class ImportResult:
    """Отчёт об импорте: что получилось, что нет.

    Не бросаем исключение на первой ошибке — собираем отчёт,
    чтобы пользователь видел «10 ок, 2 ошибки» и мог исправить файл.
    """
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[dict] = field(default_factory=list)  # [{"row": 5, "message": "..."}]
