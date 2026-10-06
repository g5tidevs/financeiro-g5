from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contas/", include("apps.contas.urls")),
    path("cadastros/", include("apps.cadastros.urls")),
    path("pix/", include("apps.pix.urls")),
    path("estornos/", include("apps.estornos.urls")),
    path("links/", include("apps.links.urls")),
    path("", include("apps.core.urls")),
]