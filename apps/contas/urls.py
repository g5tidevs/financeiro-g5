from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "contas"

urlpatterns = [
    path(
        "entrar/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
        name="login",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),

    # Cadastro de usuários (só o administrador)
    path("usuarios/", views.UsuarioListView.as_view(), name="usuarios"),
    path("usuarios/novo/", views.UsuarioCreateView.as_view(), name="usuario_novo"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario_editar"),
    path("usuarios/<int:pk>/senha/", views.UsuarioSenhaView.as_view(), name="usuario_senha"),
    path("usuarios/<int:pk>/alternar/", views.UsuarioAlternarView.as_view(), name="usuario_alternar"),
]