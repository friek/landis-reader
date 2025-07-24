import logging
import os

import paho.mqtt.client as mqtt

from p1.reader import Reader

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class SocketClosedException(Exception):
    pass


# noinspection PyUnusedLocal
def on_disconnect(client, userdata, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        raise SocketClosedException(f"MQTT socket closed with exit code {rc}")


if __name__ == '__main__':
    client = mqtt.Client()
    client.connect(host=os.getenv("MQTT_HOST"), port=int(os.getenv("MQTT_PORT", 1883)))
    client.on_disconnect = on_disconnect
    client.loop_start()

    p1_reader = Reader(port=os.getenv("P1_PORT"))
    topic = os.getenv("ENERGY_TOPIC")
    raw_topic = os.getenv("ENERGY_RAW_TOPIC")

    for message, raw_message in p1_reader.read_forever():
        if topic:
            client.publish(topic=topic, payload=message.to_json())
        if raw_topic:
            client.publish(topic=raw_topic, payload=raw_message)
        LOGGER.info("Broadcasted message")
