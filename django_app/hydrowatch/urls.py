from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("reports/", include("reports.urls")),
    path("alerts/", include("alerts.urls")),
    path("api/", include("api.urls")),
]
