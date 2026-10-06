from django.urls import path

from . import views

app_name = "estornos"

urlpatterns = [
    path("", views.EstornoListView.as_view(), name="lista"),
    path("novo/", views.EstornoCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.EstornoUpdateView.as_view(), name="editar"),
    path("<int:pk>/safra/", views.EstornoAlternarView.as_view(campo="solicitado_banco"), name="safra"),
    path("<int:pk>/conciliar/", views.EstornoAlternarView.as_view(campo="conciliado"), name="conciliar"),
    path("<int:pk>/excluir/", views.EstornoExcluirView.as_view(), name="excluir"),
]