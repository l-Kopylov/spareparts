# Spareparts

# 🚗 Spare Parts — B2B Catalog & Avito Automation

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green?logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker&logoColor=white)](https://docker.com)
[![Coverage](https://img.shields.io/badge/Coverage-94%25-brightgreen)]()

> **Backend-сервис для управления каталогом автозапчастей (колёса, авто, мото) с автоматической подготовкой фото и выгрузкой на Авито.**

## 💡 Идея проекта

Менеджеры фотографируют детали с телефона в локальной сети, заполняют карточку товара. Система **автоматически**:
1. Оптимизирует фото (ресайз до 1920×1080, сжатие JPEG).
2. Загружает их в **VK Cloud S3** с публичным доступом.
3. Генерирует **XML-фид** с прямыми ссылками на фото для автозагрузки на Авито.

## ✨ Ключевые особенности (и почему это интересно)

*   **Слоистая архитектура:** чёткое разделение на домен (`catalog`), представления (`showcase`, `adminpanel`) и интеграции (`avito_export`).
*   **Динамические формы:** поля шин и дисков скрываются и валидируются в зависимости от типа товара (`product_form`). Единый источник правды — `dicts.py` (SSOT).
*   **Интеграция с S3:** `boto3` + `Pillow`. Фото оптимизируются, загружаются с `ACL="public-read"`, публичный URL сохраняется в БД.
*   **XML-экспорт:** паттерны **Strategy**, **Mapper** и **DTO**. Генерирует теги `<Images>` с публичными ссылками.
*   **Тесты:** **68 тестов**, покрытие **~94%**. Тесты выявили реальные баги (`None vs ""`, N+1, `IntegrityError` на FK).
*   **12-factor:** настройки через `.env`, `debug-toolbar` только в `DEBUG`.

## 🏗️ Технологический стек

*   **Backend:** Python 3.12, Django 5.2
*   **База данных:** PostgreSQL 16
*   **Инфраструктура:** Docker, Docker Compose
*   **Облако/Интеграции:** VK Cloud Object Storage (S3), boto3, Pillow
*   **Тестирование:** pytest, pytest-django, factory-boy
*   **Фильтрация:** django-filter

## 🚀 Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/l-Kopylov/spareparts.git
cd spareparts

# 2. Настроить переменные окружения
cp .env.example .env
# Отредактируй .env: SECRET_KEY, DATABASE_URL, VK_S3_*

# 3. Запустить в Docker
docker compose up -d --build

# 4. Применить миграции и создать суперпользователя
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# 5. Открыть в браузере
# Панель управления: http://localhost:8000/panel/
# Каталог: http://localhost:8000/