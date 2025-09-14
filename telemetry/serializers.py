from rest_framework import serializers
from .models import Telemetry, Command


class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ["id", "device_id", "topic", "payload", "metric", "value", "ts"]


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ["id", "device_id", "command_type", "payload", "ts", "status"]
