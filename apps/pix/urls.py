from django.urls import path

from . import views

app_name = "pix"

urlpatterns = [
    path("", views.PixListView.as_view(), name="lista"),
    path("nova/", views.PixCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.PixUpdateView.as_view(), name="editar"),
]