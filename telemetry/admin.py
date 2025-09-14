from django.contrib import admin
from .models import Telemetry, Command


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ("ts", "device_id", "metric", "value")
    list_filter = ("device_id", "metric")
    search_fields = ("device_id",)


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("ts", "device_id", "command_type", "status")
    list_filter = ("device_id", "status")
    search_fields = ("device_id", "command_type")


# Register your models here.
