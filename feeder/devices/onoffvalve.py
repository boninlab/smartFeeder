#!/usr/bin/python3
from fddevice import FdDevice
import time

g_checkValveStatus = False  # 테스트용 (False:밸브 check pass)


class OnoffValve(FdDevice):
  def __init__(self, config):
    global g_tastFlag
    super().__init__(config)
    self.cyclicReadInfo = {'atype': 'actuatorValue'}
    self.ch = int(self.params[0])
    self.onStatusCh = int(self.params[1])
    self.offStatusCh = int(self.params[2])
    self.limitSec = 20  # 밸브 상태 기다림 시간 한계
    self.lastWriteValue = None  # 마지막 명령
    self.lastWritTs = None  # 마지막 명령 시간
    self.onStatus = False
    self.offStatus = False

  def writeOnoff(self, value):
    if self.actuator.slotStartOffset is not None:
      act = {'atype': 'modbus', 'slaveid': self.actuator.slaveId,
             'func': 5, 'offset': self.actuator.slotStartOffset + self.ch, 'value': value}
      self.putAction(act)

  def checkAction(self):
    if self.waitDevSignal == True:
      if g_checkValveStatus == False:
        self.signalToTask.append({self.type: 200})
        return super().checkAction()
      if self.lastWriteValue:  # 확인 원하는 상태가 True면
        if self.subActuators[0].value is not None:
          if self.subActuators[0].value[self.onStatusCh] == True:  # onStatus가 True면
            self.signalToTask.append({self.type: 200})
      else:
        if self.subActuators[1].value is not None:
          if self.subActuators[1].value[self.offStatusCh] == True:  # offStatus가 True면
            self.signalToTask.append({self.type: 200})
      if (time.time()-self.lastWritTs) > self.limitSec:
        self.signalToTask.append(
            {self.type: 500, 'msg': 'valve check timeout'})  # 에러 상황
        return super().checkAction()
      # time.sleep(1)  # 테스트용 (수동으로 명령을 주기위한 시간)
    return super().checkAction()

  def parse(self, act, value):
    if act['atype'] == 'actuatorValue':
      self.value = value[self.ch]

  def command(self, cmd):
    reCmd = False
    if cmd == 'open' or cmd == 'blower' or cmd == 'on':  # False: close, water, off
      reCmd = True
    self.lastWriteValue = reCmd
    self.lastWritTs = time.time()
    self.writeOnoff(reCmd)
