#!/usr/bin/python3
import threading
import json
from mqtthelper import *


class FdReceiver(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.c = mqttCilent('localhost', 1883, 'fdRecv')
    self.subTopic = 'feeder/#'
    self.msgs = []
    print("Receiver activated")

  def run(self):
    self.c.subscribe(self.subTopic)
    self.c.on_message = self.on_message
    self.c.loop_forever()

  def on_message(self, client, userdata, msg):
    payload = msg.payload.decode('utf-8').replace("'", '"')
    try:
      msgj = json.loads(payload)
    except Exception as ex:
      print(ex)
      return
    topics = msg.topic.split("/")
    # append({'task': {'cmd': {'params': {'cmd': 'resume'}}}})
    self.msgs.append({topics[1]: {topics[2]: msgj}})

  def hasMessage(self):
    if len(self.msgs) > 0:
      return True
    return False

  def popMessage(self):
    return self.msgs.pop()
