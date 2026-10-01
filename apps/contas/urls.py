from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm

app_name = "contas"

urlpatterns = [
    path(
        "entrar/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
]