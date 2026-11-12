from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("part/<str:kind>/<int:pk>/", views.product_detail, name="product_detail"),
]
