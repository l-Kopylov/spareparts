def active_kind(request):
    if request.path != "/":
        return {"active_kind": None}
    return {"active_kind": request.GET.get("kind", "auto")}
