from django.urls import path

from . import views

app_name = "links"

urlpatterns = [
    path("", views.LinkListView.as_view(), name="lista"),
    path("novo/", views.LinkCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.LinkUpdateView.as_view(), name="editar"),
    path("<int:pk>/etapa/<slug:campo>/", views.LinkEtapaView.as_view(), name="etapa"),
    path("<int:pk>/excluir/", views.LinkExcluirView.as_view(), name="excluir"),
]