from django.urls import path

from . import views

app_name = "especie"

urlpatterns = [
    path("", views.EspecieListView.as_view(), name="lista"),
    path("<int:pk>/", views.EspecieDetalheView.as_view(), name="detalhe"),
    path("nova/", views.EspecieCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.EspecieUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.EspecieExcluirView.as_view(), name="excluir"),
]