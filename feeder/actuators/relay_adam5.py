#!/usr/bin/python3
from fdactuator import FdActuator
from fddevice import FdDevice


class RelayAdam5(FdActuator, FdDevice):
  def __init__(self, connInfo):
    self.mqttTopic = 'act'
    FdActuator.__init__(self, connInfo)
    FdDevice.__init__(self, connInfo)
    self.slotId = int(self.params[1])
    spCh = self.params[2].split(':')
    self.sCh = int(spCh[0])  # 시작 채널
    self.eCh = int(spCh[1])  # 끝 채널
    self.readLength = 8
    if self.eCh > 7:
      self.readLength = 16
    self.slotStartOffset = None

  def readStartOffset(self):  # 슬롯 시작 주소 읽기
    act = {'atype': 'modbus', 'func': 3, 'slaveid': self.slaveId,
           'offset': 10020+(self.slotId*2), 'length': 2}
    self.putAction(act)

  def checkAction(self):
    if self.slotStartOffset is None:
      self.readStartOffset()
    return super().checkAction()

  def parse(self, act, value):
    if act['func'] == 3:  # readStartOffset
      result = value.registers
      self.slotStartOffset = result[0] - 1
      self.cyclicReadInfo = {'atype': 'modbus', 'slaveid': self.slaveId,
                             'func': 1, 'offset': self.slotStartOffset, 'length': self.readLength}
    elif act['func'] == 1:
      out = 0
      self.value = value.bits[self.sCh:self.eCh+1]
      #print(self.type+":", self.value)
