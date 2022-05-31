#!/usr/bin/python3
from fddevice import FdDevice
import time


class RotationMotor(FdDevice):
  def __init__(self, config):
    super().__init__(config)
    self.cyclicReading = False
    self.slaveId = int(self.params[0])
    self.ch = int(self.params[1])
    self.cmdFreq = None  # 명령 받은 주파수
    self.freq = 0  # 설정할 주파수
    self.cyclicReading = False
    self.cyclicReadInfo = {'atype': 'modbus', 'func': 3,
                           'slaveid': self.slaveId, 'offset': 0x000F-1, 'length': 1}  # Read Trip
    # ---------- 근접센서
    self.lastHitTS = 0  # hit 시간 오류
    self.lastCmdTS = None  # 시작 시간 오류
    self.limitSec = 10  # hit 시간 한계
    self.totalHitCount = 50  # 총 칸 수
    self.proxiReverse = False  # 근접센서 Hit reverse (default Hit = True)
    if 'options' in config:
      if config['options'].split(',')[0] == 'true':
        self.proxiReverse = True
    self.proxiSenStatus = None
    self.initStatus = None  # 초기 상태
    self.count = 0     # 근접센서 칸 확인 수
    self.ctime = 0     # 근접센서 감지 시작시간

  def readSenStatus(self):
    act = {'atype': 'actuatorValue', 'actuator': self.subActuators[0]}
    return act

  def checkHit(self):
    b = self.proxiSenStatus
    if b is None:
      return False
    if self.initStatus:
      if b == False:
        self.initStatus = False
      return False
    if b == True:
      if self.ctime == 0:
        self.ctime = time.time()
        self.count = self.count+1
        print(self.type, "proxiSen HIT", self.count)
        return True
      else:
        # check limit
        if (time.time()-self.ctime) > 0.5:
          self.ctime = 0
    else:
      if self.ctime > 0:
        self.ctime = 0
    return False

  def checkAction(self):
    if self.cmdFreq != None:
      self.putAction(self.actuator.motorOff(self.slaveId))
      if self.cmdFreq > 0:
        self.putAction(self.actuator.writeFreq(self.slaveId, self.cmdFreq*100))
        self.putAction(self.actuator.readFreq(self.slaveId))
        self.lastCmdTS = time.time()  # 최초 명령 시작 시간 기록
      else:
        self.freq = 0
      self.cmdFreq = None

    if self.freq != None:
      if self.freq > 0:  # on
        self.initStatus = self.proxiSenStatus  # 근접 센서 초기 상태 기록
        self.lastHitTS = time.time()  # 최초 hit 대기 시작 시간 기록
        self.count = 0
        self.putAction(self.actuator.motorOn(self.slaveId))
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
      self.lastCmdTS = None
      if self.on:
        if self.actuator.on == False:
          self.putAction(self.actuator.motorOn(self.slaveId))
          self.putAction(self.actuator.readStatus(self.slaveId))
      else:
        if self.actuator.on == False:
          self.cyclicReading = False
          self.active = False
          if self.waitDevSignal == True:
            self.signalToTask.append({self.type: 200})  # TASK에 종료 보고
        else:
          self.putAction(self.actuator.motorOff(self.slaveId))
          self.putAction(self.actuator.readStatus(self.slaveId))

    if self.cyclicReading:
      self.putAction(self.readSenStatus())
      hit = self.checkHit()
      if hit:
        self.lastHitTS = time.time()
        if self.count > self.totalHitCount-1:
          self.cmdFreq = 0
          self.cyclicReading = False
      if (time.time() - self.lastHitTS) >= self.limitSec:
        print(self.type, "hit 사이 시간 초과")
        self.signalToTask.append(
            {self.type: 500, 'msg': 'feeder proxiSensor hit timeout'})  # hit 사이 시간 초과
        self.cmdFreq = 0
        self.cyclicReading = False

    if self.lastCmdTS != None:
      if (time.time() - self.lastCmdTS) >= self.limitSec:
        print(self.type, "명령 시간 제한 초과")
        self.signalToTask.append(
            {self.type: 500, 'msg': 'feeder command timeout'})  # 명령 받은 뒤 시간 제한 초과
        self.lastCmdTS = None
        self.cmdFreq = 0
        self.cyclicReading = False

    return super().checkAction()

  def parse(self, act, value):
    if act['atype'] == 'modbus':
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
    if act['atype'] == 'actuatorValue':
      status = value[self.ch]
      if self.proxiReverse:
        if status:
          status = False
        else:
          status = True
      self.proxiSenStatus = value[self.ch]

  def command(self, cmd):
    if isinstance(cmd, dict):
      if 'count' in cmd:
        self.totalHitCount = int(cmd['count'])
      cmd = cmd['value']
      if cmd == 'off':
        cmd = 0
      self.cmdFreq = int(cmd)
    else:
      if cmd == 'off':
        cmd = 0
      self.cmdFreq = cmd
