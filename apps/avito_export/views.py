# apps/avito_export/views.py
"""Вьюхи выгрузки/загрузки Авито.

Доступ: только staff (админ + менеджер) — @staff_member_required.
"""
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render

from apps.catalog.models import Wheel, AutoPart, MotoPart
from .services.avito_xml import AvitoXmlExporter, AvitoXmlImporter

logger = logging.getLogger("avito_export")

# kind -> (queryset, человекочитаемое имя, иконка)
EXPORT_KINDS = {
    "wheel": (lambda: Wheel.objects.filter(is_active=True).order_by("pk"),
              "Колёса и шины", "bi-disc"),
    "auto": (lambda: AutoPart.objects.filter(is_active=True).order_by("pk"),
             "Детали для авто", "bi-car-front-fill"),
    "moto": (lambda: MotoPart.objects.filter(is_active=True).order_by("pk"),
             "Детали для мото", "bi-bicycle"),
}


@staff_member_required
def export_page(request):
    """Страница выбора: колёса / авто / мото."""
    kinds = [
        (kind, label, icon, qs().count())
        for kind, (qs, label, icon) in EXPORT_KINDS.items()
    ]
    return render(request, "avito_export/export.html", {"kinds": kinds})


@staff_member_required
def export_view(request, kind):
    """Скачать XML-фид по типу (wheel / auto / moto)."""
    if kind not in EXPORT_KINDS:
        return HttpResponse("Неизвестный тип", status=404)

    qs, label, _ = EXPORT_KINDS[kind]
    items = list(qs())
    xml = AvitoXmlExporter().export(items)

    logger.info("export_download user=%s kind=%s count=%d bytes=%d",
                request.user.username, kind, len(items), len(xml))

    filename = f"avito_{kind}.xml"
    response = HttpResponse(xml, content_type="application/xml; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

@staff_member_required
def import_view(request, kind="wheel"):
    """Загрузить XML-фид для kind (wheel/auto/moto). Показать отчёт."""
    if kind not in ("wheel", "auto", "moto"):
        return HttpResponse("Неизвестный тип", status=404)

    result = None
    error = None

    if request.method == "POST":
        f = request.FILES.get("file")
        if not f:
            error = "Выберите файл"
        elif not f.name.lower().endswith(".xml"):
            error = "Нужен файл .xml"
        else:
            try:
                importer = AvitoXmlImporter()
                items = importer.parse(f)
                batch_name = request.POST.get("batch_name", "").strip() or "Без названия"

                logger.info("import_upload user=%s kind=%s filename=%s size=%d batch=%r rows=%d",
                            request.user.username, kind, f.name, f.size, batch_name, len(items))

                result = importer.import_to_db(items, batch_name=batch_name, kind=kind)

                logger.info("import_done user=%s kind=%s total=%d created=%d updated=%d skipped=%d",
                            request.user.username, kind, result.total, result.created,
                            result.updated, result.skipped)
            except Exception as e:
                logger.error("import_error user=%s kind=%s filename=%s",
                             request.user.username, kind, f.name, exc_info=True)
                error = f"Ошибка импорта: {e}"

    return render(request, "avito_export/import.html", {
        "result": result,
        "error": error,
        "kind": kind,
    })