import json
import time
import os
import ssl
from typing import Optional

from django.core.management.base import BaseCommand
from django.utils import timezone
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

from telemetry.models import Telemetry


class Command(BaseCommand):
    help = "MQTT consumer that subscribes to telemetry topics and stores messages in DB"

    def add_arguments(self, parser):
        parser.add_argument("--host", default=None)
        parser.add_argument("--port", type=int, default=None)
        parser.add_argument("--username", default=None)
        parser.add_argument("--password", default=None)
        parser.add_argument("--tls", action="store_true")
        parser.add_argument("--topic", default=None)

    def handle(self, *args, **options):
        load_dotenv()

        host = options["host"] or os.getenv("MQTT_HOST", "broker.emqx.io")
        port = options["port"] or int(os.getenv("MQTT_PORT", "1883"))
        username = options["username"] or os.getenv("MQTT_USERNAME")
        password = options["password"] or os.getenv("MQTT_PASSWORD")
        use_tls = options["tls"] or os.getenv("MQTT_TLS", "false").lower() == "true"
        topic = options["topic"] or os.getenv(
            "MQTT_TELEMETRY_TOPIC", "devices/+/telemetry"
        )

        client_id = os.getenv("MQTT_CLIENT_ID", f"drf-dashboard-{int(time.time())}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Connecting to MQTT {host}:{port}, topic '{topic}', TLS={use_tls}"
            )
        )

        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        if username and password:
            client.username_pw_set(username, password)
        if use_tls:
            client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

        def on_connect(client, userdata, flags, reason_code, properties=None):
            self.stdout.write(self.style.SUCCESS(f"Connected with code {reason_code}"))
            client.subscribe(topic)

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode("utf-8")
                data = json.loads(payload)
            except Exception as e:
                self.stderr.write(f"Failed to parse JSON: {e}; payload={msg.payload!r}")
                return

            device_id = data.get("device_id") or data.get("device") or "unknown"
            metric = data.get("metric")
            value = data.get("value")
            ts_str = data.get("ts")
            ts = None
            if ts_str:
                try:
                    ts = timezone.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except Exception:
                    ts = None
            if ts is None:
                ts = timezone.now()

            Telemetry.objects.create(
                device_id=device_id,
                topic=msg.topic,
                payload=data,
                metric=metric,
                value=value,
                ts=ts,
            )
            self.stdout.write(f"Saved telemetry from {device_id} {metric=} {value=}")

        client.on_connect = on_connect
        client.on_message = on_message

        while True:
            try:
                client.connect(host, port, keepalive=60)
                client.loop_forever()
            except Exception as e:
                self.stderr.write(f"MQTT connection error: {e}; retrying in 3s...")
                time.sleep(3)
