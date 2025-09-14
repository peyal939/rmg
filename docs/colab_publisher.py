# Colab publisher for DRF + MQTT dashboard prototype
# Copy/paste into a Google Colab cell

import json, uuid, random, time, datetime
import paho.mqtt.client as mqtt

# Configure to match Django consumer defaults (.env)
BROKER = "broker.emqx.io"  # or your broker
PORT = 1883
TOPIC = "devices/{deviceId}/telemetry"

device_id = str(uuid.uuid4())[:8]
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect(BROKER, PORT, 60)

for i in range(40):
    metric = "temperature"
    value = round(random.uniform(20.0, 35.0), 2)
    payload = {
        "device_id": device_id,
        "metric": metric,
        "value": value,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
    }
    topic = TOPIC.format(deviceId=device_id)
    client.publish(topic, json.dumps(payload))
    print("Sent to", topic, payload)
    time.sleep(2)

client.disconnect()
