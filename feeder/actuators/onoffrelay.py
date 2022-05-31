#!/usr/bin/python3
from fdactuator import FdActuator


class OnOffRelay(FdActuator):
  def __init__(self, connInfo):
    self.mqttTopic = 'act'
    FdActuator.__init__(self, connInfo)
