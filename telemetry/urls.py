from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"telemetry", views.TelemetryViewSet, basename="telemetry")
router.register(r"commands", views.CommandViewSet, basename="commands")

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/", include(router.urls)),
]
