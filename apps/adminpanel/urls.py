from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel_index, name="panel_index"),
    path("new/<str:kind>/", views.new_item, name="new_item"),
    path("edit/<str:kind>/<int:pk>/", views.edit_item, name="edit_item"),
    path("delete/<str:kind>/<int:pk>/", views.delete_item, name="delete_item"),
    path("photo/<str:kind>/<int:pk>/<int:photo_id>/delete/",
         views.photo_delete, name="photo_delete"),
]
