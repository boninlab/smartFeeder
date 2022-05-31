#!/usr/bin/python3
from fdactuator import FdActuator
from fddevice import FdDevice
import time
import json


class SwitchAdam5(FdActuator, FdDevice):
  def __init__(self, connInfo):
    self.mqttTopic = 'act'
    FdActuator.__init__(self, connInfo)
    FdDevice.__init__(self, connInfo)
    self.switchConfPath = '/etc/smart-feeder/switch-conf.json'
    self.slotId = int(self.params[1])
    spCh = self.params[2].split(':')
    self.sCh = int(spCh[0])  # 시작 채널
    self.eCh = int(spCh[1])  # 끝 채널
    self.readLength = 8
    if self.eCh > 7:
      self.readLength = 16
    self.slotStartOffset = None
    self.pressIntervalSec = 0.01
    self.firstPressTs = {}
    self.swConfs = None

  def loadSwitchConf(self):
    with open(self.switchConfPath, 'r') as f:
      self.swConfs = json.load(f)[self.type]
    if self.swConfs is None:
      print("load switchConf error")

  def readStartOffset(self):  # 슬롯 시작 주소 읽기
    readStartOffset = {'atype': 'modbus', 'func': 3, 'slaveid': self.slaveId,
                       'offset': 10020+(self.slotId*2), 'length': 2}
    self.putAction(readStartOffset)

  def checkAction(self):
    if self.slotStartOffset is None:
      self.readStartOffset()
    return super().checkAction()

  def parse(self, readDic, value):
    if readDic['func'] == 3:  # readStartOffset
      result = value.registers
      self.slotStartOffset = result[0] - 1
      self.cyclicReadInfo = {'atype': 'modbus', 'slaveid': self.slaveId,
                             'func': 1, 'offset': self.slotStartOffset, 'length': self.readLength}
    elif readDic['func'] == 1:
      out = 0
      self.loadSwitchConf()
      self.value = value.bits[self.sCh:self.eCh+1]
      for idx, btn in enumerate(self.value):
        nowTs = time.time()
        if btn:
          if idx not in self.firstPressTs:
            self.firstPressTs.update({idx: nowTs})
        else:
          if idx in self.firstPressTs:
            if (nowTs - self.firstPressTs[idx]) >= (self.pressIntervalSec):
              swConf = self.swConfs[str(idx)]
              topic = ''
              if 'taskType' in swConf:
                topic = 'feeder/task/add'
              #print("- mqttPub:", topic, swConf)
              self.conn.mqtt.client.publish(topic, str(swConf), 0)
              del self.firstPressTs[idx]

      #print(self.type+":", self.value)
