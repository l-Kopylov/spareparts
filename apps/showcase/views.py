from django.shortcuts import get_object_or_404, render

from apps.catalog.models import AutoPart, MotoPart, Wheel

MODELS = {
    "auto": AutoPart,
    "moto": MotoPart,
    "wheel": Wheel,
}


def index(request):
    ctx = {
        "auto_parts": AutoPart.objects.filter(is_active=True).order_by("-created_at"),
        "moto_parts": MotoPart.objects.filter(is_active=True).order_by("-created_at"),
        "wheels": Wheel.objects.filter(is_active=True).order_by("-created_at"),
    }
    return render(request, "showcase/index.html", ctx)


def product_detail(request, kind, pk):
    model = MODELS[kind]
    item = get_object_or_404(model, pk=pk, is_active=True)
    return render(request, "showcase/product_detail.html", {"item": item})
