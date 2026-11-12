from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.forms import AutoPartForm, MotoPartForm, WheelForm, PartPhoto
from apps.catalog.models import AutoPart, MotoPart, Wheel

# kind -> (модель, форма, человекочитаемое название)
REGISTRY = {
    "auto":  (AutoPart, AutoPartForm, "Деталь для авто"),
    "moto":  (MotoPart, MotoPartForm, "Деталь для мото"),
    "wheel": (Wheel, WheelForm, "Колёса и шины"),
}


def _ctx(kind, form, instance=None):
    model, _, title = REGISTRY[kind]
    ctx = {"kind": kind, "title": title, "form": form}
    if instance:
        ctx["item"] = instance
        ctx["photos"] = instance.photos.all()
    return ctx


@staff_member_required
def panel_index(request):
    return render(request, "adminpanel/index.html", {
        "auto_parts": AutoPart.objects.order_by("-created_at"),
        "moto_parts": MotoPart.objects.order_by("-created_at"),
        "wheels": Wheel.objects.order_by("-created_at"),
        "report_url": "/panel/avito/report/",
    })


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def delete_item(request, kind, pk):
    model, _, _ = REGISTRY[kind]
    item = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect("panel_index")
    return render(request, "adminpanel/delete_confirm.html",
                  {"kind": kind, "item": item})


@staff_member_required
def photo_delete(request, kind, pk, photo_id):
    # удаление отдельного фото при редактировании
    photo = get_object_or_404(PartPhoto, pk=photo_id, object_id=pk)
    if request.method == "POST":
        photo.image.delete(save=False)
        photo.delete()
    return redirect("edit_item", kind=kind, pk=pk)
