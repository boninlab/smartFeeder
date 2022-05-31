#!/usr/bin/python3

class FdActuator:
  def __init__(self, config):
    self.conn = None
    self.type = config.name  # section name
    if 'connParameter' in config:
      self.params = config['connParameter'].split(',')
      self.slaveId = int(self.params[0])
