from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "cadastros"

urlpatterns = [
    path("", RedirectView.as_view(url="lojas/"), name="inicio"),
    path("<slug:entidade>/", views.CadastroListView.as_view(), name="lista"),
    path("<slug:entidade>/novo/", views.CadastroCreateView.as_view(), name="novo"),
    path("<slug:entidade>/<int:pk>/editar/", views.CadastroUpdateView.as_view(), name="editar"),
    path("<slug:entidade>/<int:pk>/alternar/", views.CadastroAlternarView.as_view(), name="alternar"),
]