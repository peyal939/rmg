from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import Telemetry, Command
from .serializers import TelemetrySerializer, CommandSerializer
from .publish import publish_command
from django.views.decorators.http import require_GET


@require_GET
def dashboard(request):
    return render(request, "dashboard.html")


# Placeholder ViewSets to wire later
class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = TelemetrySerializer
    queryset = Telemetry.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        device_id = self.request.query_params.get("device_id")
        metric = self.request.query_params.get("metric")
        since = self.request.query_params.get("since")
        until = self.request.query_params.get("until")
        if device_id:
            qs = qs.filter(device_id=device_id)
        if metric:
            qs = qs.filter(metric=metric)
        if since:
            dt = parse_datetime(since)
            if dt:
                qs = qs.filter(ts__gte=dt)
        if until:
            dt = parse_datetime(until)
            if dt:
                qs = qs.filter(ts__lte=dt)
        return qs.order_by("ts")


class CommandViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommandSerializer
    queryset = Command.objects.all()

    def create(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        command = request.data.get("command") or request.data.get("command_type")
        value = request.data.get("value")
        if not device_id or not command:
            return Response(
                {"detail": "device_id and command are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {"device_id": device_id, "command": command}
        if value is not None and value != "":
            payload["value"] = value

        cmd = Command.objects.create(
            device_id=device_id, command_type=command, payload=payload, status="queued"
        )
        try:
            publish_command(device_id, command, value)
            cmd.status = "sent"
            cmd.save(update_fields=["status"])
        except Exception as e:
            cmd.status = "failed"
            cmd.save(update_fields=["status"])
            return Response(
                {"detail": f"Publish failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY
            )
        ser = CommandSerializer(cmd)
        return Response(ser.data, status=status.HTTP_201_CREATED)


# Create your views here.
