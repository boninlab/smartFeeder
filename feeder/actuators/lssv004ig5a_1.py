#!/usr/bin/python3
from fdactuator import FdActuator
from fddevice import FdDevice


class LsSv004ig5a_1(FdActuator):
  def __init__(self, connInfo):
    self.mqttTopic = 'speed'
    self.on = False
    super().__init__(connInfo)

  def writeFreq(self, slaveId, value):  # 주파수 설정
    act = {'atype': 'modbus', 'slaveid': slaveId,
           'func': 6, 'offset': 0x0005-1, 'value': value}
    return act

  def readFreq(self, slaveId):  # 설정된 주파수 확인
    act = {'atype': 'modbus', 'func': 3, 'slaveid': slaveId,
           'offset': 0x0005-1, 'length': 1}
    return act

  def motorOn(self, slaveId, reverse=False):
    val = 2
    if reverse == True:
      val = 4
    act = {'atype': 'modbus', 'slaveid': slaveId,
           'func': 6, 'offset': 0x0006-1, 'value': val}
    return act

  def motorOff(self, slaveId):
    act = {'atype': 'modbus', 'slaveid': slaveId,
           'func': 6, 'offset': 0x0006-1, 'value': 1}
    return act

  def readStatus(self, slaveId):  # On/Off 상태 확인
    act = {'atype': 'modbus', 'func': 3, 'slaveid': slaveId,
           'offset': 0x0006-1, 'length': 1}
    return act
