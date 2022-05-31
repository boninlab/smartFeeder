#!/usr/bin/python3
import time


class FdDevice:
  lastRetry = 0  # retry counter for communication

  def __init__(self, config):
    self.actuator = None
    self.subActuators = None  # 1개 초과의 actuator를 사용할 경우(obj list)
    self.type = config.name
    self.logger = None
    self.acts = []
    self.value = None
    if 'connParameter' in config:
      self.params = config['connParameter'].split(',')
    self.writeInfo = None
    self.waitDevSignal = False  # Task로 상태 전송 여부
    self.signalToTask = []  # Task로 보낼 신호
    # ------------------------------------------------ readParams
    self.cyclicReading = True
    self.cyclicReadInfo = None
    self.lastReadtime = 0
    self.readInterval = 1000  # ms
    if 'readInterval' in config:
      self.readInterval = int(config['readInterval'])

  def checkAction(self):
    if self.cyclicReading == True:
      nowTs = time.time()
      if (nowTs - self.lastReadtime) >= (self.readInterval / 1000):
        self.lastReadtime = nowTs
        if self.cyclicReadInfo is not None:
          self.putAction(self.cyclicReadInfo)

  def hasAction(self):
    return len(self.acts) > 0

  def putAction(self, act):
    if not act in self.acts:  # 중복 act 무시
      self.acts.append(act)

  def getAction(self):
    if len(self.acts) > 0:
      return self.acts.pop(0)
    return None

  def command(self, cmd):
    return False
