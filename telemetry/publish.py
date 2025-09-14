import json
import os
import ssl
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt


def publish_command(device_id: str, command: str, value=None):
    load_dotenv()
    host = os.getenv("MQTT_HOST", "broker.emqx.io")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    tls = os.getenv("MQTT_TLS", "false").lower() == "true"
    topic_tpl = os.getenv("MQTT_COMMAND_TOPIC", "devices/{deviceId}/commands")
    topic = topic_tpl.format(deviceId=device_id)

    payload = {"device_id": device_id, "command": command}
    if value is not None and value != "":
        payload["value"] = value

    client = mqtt.Client(protocol=mqtt.MQTTv5)
    if username and password:
        client.username_pw_set(username, password)
    if tls:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    client.connect(host, port, 60)
    client.publish(topic, json.dumps(payload))
    client.disconnect()

    return {"topic": topic, "payload": payload}
