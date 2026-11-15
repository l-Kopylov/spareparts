
# apps/avito_export/validators.py
"""Валидация FeedItem до записи в БД."""
from .services.schemas import FeedItem
from apps.catalog.dicts import ALLOWED_CATEGORIES


def validate_feed_item(item: FeedItem, kind: str = "wheel") -> list[str]:
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

    # Проверка категории: для kind="auto" — только PART_TYPES_AUTO
    allowed = ALLOWED_CATEGORIES.get(kind, [])
    if item.category and allowed and item.category not in allowed:
        errors.append(
            f"Категория «{item.category}» не моя для kind={kind} "
            f"(допустимо: {', '.join(allowed[:5])}...)"
        )

    return errors

    # Проверка: категория существует в БД для kind
    if kind == "auto":
        from apps.catalog.models import Category
        if not Category.objects.filter(name=item.category, scope="auto").exists():
            errors.append(f"Категория «{item.category}» не найдена в БД (scope=auto)")
    elif kind == "moto":
        from apps.catalog.models import Category
        if not Category.objects.filter(name=item.category, scope="moto").exists():
            errors.append(f"Категория «{item.category}» не найдена в БД (scope=moto)")