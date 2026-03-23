from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"stations", views.StationViewSet)
router.register(r"readings", views.WaterLevelReadingViewSet)
router.register(r"alerts", views.AlertRuleViewSet)
router.register(r"alert-events", views.AlertEventViewSet)
router.register(r"reports", views.ReportViewSet)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
