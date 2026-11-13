from django.shortcuts import get_object_or_404, render
from django.http import Http404

from apps.catalog.models import AutoPart, MotoPart, Wheel

MODELS = {
    "auto": AutoPart,
    "moto": MotoPart,
    "wheel": Wheel,
}


KIND_LABELS = {
    "auto": "Детали для авто",
    "moto": "Детали для мото",
    "wheel": "Колёса и шины",
}


def index(request):
    kind = request.GET.get("kind", "auto")  # по умолчанию — авто
    if kind not in MODELS:  # защита от ?kind=unknown
        kind = "auto"

    model = MODELS[kind]
    items = model.objects.filter(is_active=True).order_by("-created_at")

    ctx = {
        "kind": kind,
        "kind_label": KIND_LABELS[kind],
        "items": items,
    }
    return render(request, "showcase/index.html", ctx)


def product_detail(request, kind, pk):
    model = MODELS.get(kind)
    if model is None:
        raise Http404("Неизвестный тип детали")
    item = get_object_or_404(model, pk=pk, is_active=True)
    return render(request, "showcase/product_detail.html", {"item": item})