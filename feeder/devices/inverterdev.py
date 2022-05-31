#!/usr/bin/python3
from fddevice import FdDevice


class InverterDev(FdDevice):
  def __init__(self, config):
    super().__init__(config)
    self.cyclicReading = False
    self.slaveId = int(self.params[0])
    self.cmdFreq = None  # 명령 받은 주파수
    self.freq = None  # 설정된 주파수
    self.cyclicReading = False
    self.cyclicReadInfo = {'atype': 'modbus', 'func': 3,
                           'slaveid': self.slaveId, 'offset': 0x000F-1, 'length': 1}  # Read Trip
    self.inverterReverse = False  # 역회전
    if 'options' in config:
      if config['options'].split(',')[0] == 'true':
        self.inverterReverse = True
    self.active = False
    self.on = False

  def checkAction(self):
    if self.cmdFreq != None:
      self.putAction(self.actuator.motorOff(self.slaveId))
      self.putAction(self.actuator.writeFreq(self.slaveId, self.cmdFreq*100))
      self.putAction(self.actuator.readFreq(self.slaveId))
      self.cmdFreq = None

    if self.freq != None:
      if self.freq > 0:  # on
        self.putAction(self.actuator.motorOn(
            self.slaveId, reverse=self.inverterReverse))
        self.putAction(self.actuator.readStatus(self.slaveId))
        self.cyclicReading = True  # Read Trip
        self.active = True
        self.on = True
      else:  # off
        self.putAction(self.actuator.motorOff(self.slaveId))
        self.putAction(self.actuator.readStatus(self.slaveId))
        self.active = True
        self.on = False
      self.freq = None

    if self.active:
      if self.on:
        if self.actuator.on == False:
          self.putAction(self.actuator.motorOn(
              self.slaveId, reverse=self.inverterReverse))
          self.putAction(self.actuator.readStatus(self.slaveId))
      else:
        if self.actuator.on == False:
          self.cyclicReading = False
          self.active = False
        else:
          self.putAction(self.actuator.motorOff(self.slaveId))
          self.putAction(self.actuator.readStatus(self.slaveId))

    return super().checkAction()

  def parse(self, act, value):
    if act['func'] == 3:
      result = value.registers
      if act['offset'] == 0x0005-1:  # freq
        self.freq = result[0]/100
        self.cmdFreq = None
      elif act['offset'] == 0x0006-1:  # status
        if (result[0] & 1) != 0:
          self.actuator.on = False
        elif (result[0] & 2) != 0:
          self.actuator.on = True
        elif (result[0] & 4) != 0:  # 역방향 ON
          self.actuator.on = True
      elif act['offset'] == 0x000F-1:  # trip
        if result[0] != 0:
          print(self.type, "Trip error!", result[0])

  def command(self, cmd):
    if cmd == 'off':
      cmd = 0
    self.cmdFreq = cmd
