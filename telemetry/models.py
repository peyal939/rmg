from django.db import models


class Telemetry(models.Model):
    device_id = models.CharField(max_length=128, db_index=True)
    topic = models.CharField(max_length=255, blank=True, default="")
    payload = models.JSONField()
    metric = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    value = models.FloatField(null=True, blank=True)
    ts = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-ts"]

    def __str__(self):
        return f"{self.device_id} {self.metric}@{self.ts}"


class Command(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    device_id = models.CharField(max_length=128, db_index=True)
    command_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    ts = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="queued")

    class Meta:
        ordering = ["-ts"]

    def __str__(self):
        return f"{self.device_id} {self.command_type} ({self.status})"


# Create your models here.
