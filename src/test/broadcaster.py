import logging
import os
from time import sleep

import paho.mqtt.client as mqtt

from p1.converter import Converter

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    client = mqtt.Client()
    # client.connect("2a02:58:4:2::10")
    client.connect("192.168.11.10")
    # client.connect("localhost")
    client.loop_start()

    with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'reading-201912022211.txt')) as f:
        contents = f.read()
        converter = Converter()
        result = converter.convert_p1_message(contents)

    if result:
        json = result.to_json()
    else:
        json = '{}'

    while True:
        try:
            client.publish("localhost/energy", payload=json)
            LOGGER.info("Broadcasted message")
        except:
            LOGGER.exception("Exception caught")

        sleep(10)
