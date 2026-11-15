from django.urls import path
from . import views

urlpatterns = [
    path("export/", views.export_page, name="avito_export_page"),
    path("export/<str:kind>/", views.export_view, name="avito_export"),
    path("import/", views.import_view, name="avito_import"),  # default wheel
    path("import/<str:kind>/", views.import_view, name="avito_import_kind"),
]