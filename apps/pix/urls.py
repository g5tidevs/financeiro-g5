from django.urls import path

from . import views

app_name = "pix"

urlpatterns = [
    path("", views.PixListView.as_view(), name="lista"),
    path("<int:pk>/", views.PixDetalheView.as_view(), name="detalhe"),
    path("nova/", views.PixCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.PixUpdateView.as_view(), name="editar"),
    path("<int:pk>/conciliar/", views.PixConciliarView.as_view(), name="conciliar"),
    path("<int:pk>/excluir/", views.PixExcluirView.as_view(), name="excluir"),
]