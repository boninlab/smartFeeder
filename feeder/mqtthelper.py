#!/usr/bin/python3
from paho.mqtt import client as mqtt_client
import threading


class MqttObj(threading.Thread):
  def __init__(self, host, port, clientId):
    threading.Thread.__init__(self)
    self.client = mqtt_client.Client(clientId)
    self.host = str(host)
    self.port = int(port)

  def run(self):
    self.client.connect(self.host, self.port)
    self.client.loop_forever()


def mqttCilent(host, port, clientId):
  client = mqtt_client.Client(clientId)
  client.connect(host, port)
  return client
