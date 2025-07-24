FROM python:3.13

RUN --mount=type=bind,source=src/requirements.txt,target=/tmp/requirements.txt \
  pip install --requirement /tmp/requirements.txt

COPY src/ /application/

ENV MQTT_HOST=localhost
ENV MQTT_PORT=1883
ENV P1_PORT="/dev/ttyUSB0"

CMD ["/usr/local/bin/python", "/application/main.py"]
