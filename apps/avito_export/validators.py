
# apps/avito_export/validators.py
"""Валидация FeedItem до записи в БД.

Возвращает список ошибок (пусто = ок). Не пишет в БД, не бросает исключения.
"""
from .services.schemas import FeedItem


def validate_feed_item(item: FeedItem) -> list[str]:
    """Проверить одну строку фида. Вернуть список ошибок (строк)."""
    errors = []

    if not item.external_id:
        errors.append("Id обязателен")
    if not item.title:
        errors.append("Title обязателен")
    elif len(item.title) > 50:
        errors.append(f"Title длиннее 50 символов ({len(item.title)})")
    if not item.description:
        errors.append("Description обязателен")
    elif len(item.description) > 3000:
        errors.append(f"Description длиннее 3000 символов ({len(item.description)})")
    if item.price is None or item.price <= 0:
        errors.append(f"Price должен быть > 0 (сейчас {item.price})")
    if not item.category:
        errors.append("Category обязательна")
    if not item.address:
        errors.append("Address обязателен")

    return errors
