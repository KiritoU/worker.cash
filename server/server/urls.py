from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(f"{settings.DJANGO_ADMIN_URL}/", admin.site.urls),
    path("workercash/", include("workercash.urls")),
]
