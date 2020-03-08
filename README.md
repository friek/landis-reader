# Landis power meter reader

This is a simple python application which reads the output of the P1 port
of a Landis Gyr+ E350 power meter. This is currently quite a common smart power
meter in the Netherlands.

Several other Landis meters use the format this application is reading and
converting. I've only tested this with the E350, so YMMV.

## What this app does

It basically opens the USB serial port and continually reads the output from
the power meter. Every 10 seconds the meter outputs statistics and other
information from the meter, converts it to a more readable JSON format and
broadcasts it to a MQTT topic.

## Prerequisites

What you need:

* A linux box connected to the P1 port of the power meter (may as well be a
  raspberry pi)
* docker and docker-compose
* An MQTT service and the topic name to broadcast to

Copy config.dist.env to config.env, modify the values to your needs and run
```docker-compose up -d```. 

## Landis message format

To get a more detailed look at the message format of the Landis meter, look at
src/p1/converter.py. 
