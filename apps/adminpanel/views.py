from functools import wraps

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from apps.catalog.forms import AutoPartForm, MotoPartForm, WheelForm, PartPhoto
from apps.catalog.models import AutoPart, MotoPart, Wheel

REGISTRY = {
    "auto":  (AutoPart, AutoPartForm, "Деталь для авто"),
    "moto":  (MotoPart, MotoPartForm, "Деталь для мото"),
    "wheel": (Wheel, WheelForm, "Колёса и шины"),
}

KIND_PERM = {
    "auto": "autopart",
    "moto": "motopart",
    "wheel": "wheel",
}


def require_part_perm(action):
    """Проверяет право catalog.<action>_<model> в зависимости от kind."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            kind = kwargs.get("kind")
            model_name = KIND_PERM.get(kind)
            if not model_name:
                raise PermissionDenied("Неизвестный тип детали")
            perm = f"catalog.{action}_{model_name}"
            if not request.user.has_perm(perm):
                raise PermissionDenied(f"Нет права: {perm}")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def _ctx(kind, form, instance=None):
    model, _, title = REGISTRY[kind]
    ctx = {"kind": kind, "title": title, "form": form}
    if instance:
        ctx["item"] = instance
        ctx["photos"] = instance.photos.all()
    return ctx




@staff_member_required
def panel_index(request):
    """Список товаров с табами (wheel/auto/moto) и пагинацией."""
    kind = request.GET.get("kind", "wheel")
    if kind not in ("wheel", "auto", "moto"):
        kind = "wheel"

    page = request.GET.get("page", 1)

    model, _, title = REGISTRY[kind]
    qs = model.objects.order_by("-created_at")

    paginator = Paginator(qs, 20)  # 20 на страницу
    page_obj = paginator.get_page(page)

    return render(request, "adminpanel/index.html", {
        "kind": kind,
        "title": title,
        "page_obj": page_obj,
        "total": qs.count(),
    })


@require_part_perm("add")
def new_item(request, kind):
    model, form_cls, _ = REGISTRY[kind]
    if request.method == "POST":
        form = form_cls(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("panel_index")
    else:
        form = form_cls()
    return render(request, f"adminpanel/{kind}_form.html", _ctx(kind, form))


@require_part_perm("change")
def edit_item(request, kind, pk):
    model, form_cls, _ = REGISTRY[kind]
    item = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        form = form_cls(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("panel_index")
    else:
        form = form_cls(instance=item)
    return render(request, f"adminpanel/{kind}_form.html", _ctx(kind, form, item))


@require_part_perm("delete")
def delete_item(request, kind, pk):
    model, _, _ = REGISTRY[kind]
    item = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect("panel_index")
    return render(request, "adminpanel/delete_confirm.html",
                  {"kind": kind, "item": item})


@require_part_perm("change")
def photo_delete(request, kind, pk, photo_id):
    photo = get_object_or_404(PartPhoto, pk=photo_id, object_id=pk)
    if request.method == "POST":
        photo.image.delete(save=False)
        photo.delete()
    return redirect("edit_item", kind=kind, pk=pk)
