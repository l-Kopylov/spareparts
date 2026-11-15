
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.catalog.filters import AutoPartFilter, MotoPartFilter, WheelFilter
from apps.catalog.models import AutoPart, MotoPart, Wheel

MODELS = {
    "auto": AutoPart,
    "moto": MotoPart,
    "wheel": Wheel,
}

FILTERS = {
    "auto": AutoPartFilter,
    "moto": MotoPartFilter,
    "wheel": WheelFilter,
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
    qs = model.objects.filter(is_active=True).order_by("-created_at")

    filter_cls = FILTERS[kind]
    f = filter_cls(request.GET, queryset=qs)

    ctx = {
        "kind": kind,
        "kind_label": KIND_LABELS[kind],
        "items": f.qs,
        "filter": f,
    }
    return render(request, "showcase/index.html", ctx)


def product_detail(request, kind, pk):
    model = MODELS.get(kind)
    if model is None:
        raise Http404("Неизвестный тип детали")
    item = get_object_or_404(model, pk=pk, is_active=True)
    return render(request, "showcase/product_detail.html", {"item": item, "kind": kind})