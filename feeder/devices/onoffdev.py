#!/usr/bin/python3
from fddevice import FdDevice
import time


class OnoffDevice(FdDevice):
  def __init__(self, config):
    super().__init__(config)
    self.ch = int(self.params[0])

  def writeOnoff(self, value):
    act = {'atype': 'modbus', 'slaveid': self.actuator.slaveId,
           'func': 5, 'offset': self.ch, 'value': value}
    self.putAction(act)

  def command(self, cmd):
    reCmd = False
    if cmd == 'open' or cmd == 'on':  # False: close, off
      reCmd = True
    self.lastWriteValue = reCmd
    self.lastWritTs = time.time()
    self.writeOnoff(reCmd)
