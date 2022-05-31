#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from datetime import datetime
import time
import sys
import json


class modbus_VFD_LS:
  def __init__(self, rtu, addr):
    self.rtu = rtu
    self.addr = addr
    self.on = False

  def getFreq(self):
    value = self.rtu.read_holding_registers(0x0005-1, 1, unit=self.addr)
    try:
      result = value.registers
    except Exception as e:
      return None
    return result[0]/100

  def getTrip(self):
    try:
      value = self.rtu.read_holding_registers(0x000F-1, 1, unit=self.addr)
      result = value.registers
    except Exception as e:
      # print(e)
      return None
    return result[0]

  def getStatus(self):
    try:
      value = self.rtu.read_holding_registers(0x0006-1, 1, unit=self.addr)
      result = value.registers
    except:
      return 0
    if (result[0] & 1) != 0:
      self.on = False
    elif (result[0] & 2) != 0:
      self.on = True
    return result[0]

  def setFreq(self, fval):
    self.rtu.write_register(0x0005-1, int(fval*100), unit=self.addr)
    return self.getFreq()

  def motorOn(self):
    self.rtu.write_register(0x0006-1, 2, unit=self.addr)
    return self.getStatus()

  def motorOff(self):
    self.rtu.write_register(0x0006-1, 1, unit=self.addr)
    return self.getStatus()


class AdamProxiSensor:
  def __init__(self, rtu, **params):
    self.rtu = rtu
    self.reverse = params.get('reverse')
    self.addr = params.get('addr')
    self.slot = params.get('slot')
    self.ch = params.get('ch')
    self.startOffset = None
    self.last = None          # 마지막 근접센서 값
    self.tlast = None         # 마지막 근접센서 값을 얻은 시간
    self.vinit = False        # 초기 상태값
    self.count = 0            # 근접센서 칸 확인 수
    self.ctime = 0            # 근접센서 감지 시작시간

  def setInitValue(self, value):
    self.vinit = value

  def setStartOffset(self):
    value = self.rtu.read_holding_registers(
        10020+(self.slot*2), 2, unit=self.addr)
    if not hasattr(value, 'registers'):
      return None
    result = value.registers
    self.startOffset = result[0] - 1
    return self.startOffset

  def getSenStatus(self):
    status = None  # 감지됨= True
    value = self.rtu.read_coils(self.startOffset, 16, unit=self.addr)
    if not hasattr(value, 'bits'):
      return None
    status = value.bits[self.ch]
    if self.reverse:
      if status:
        status = False
      else:
        status = True
    self.last = status
    self.tlast = time.time()
    return status

  def IsSet(self):
    if self.last is None:
      return False
    return self.last

  def checkHit(self):
    b = self.getSenStatus()
    if b is None:
      return False
    if self.vinit:
      if b == False:
        self.vinit = False
      return False
    if b == True:
      if self.ctime == 0:
        self.ctime = time.time()
        self.count = self.count+1
        return True
      else:
        # check limit
        if (time.time()-self.ctime) > 1:
          self.ctime = 0
    else:
      if self.ctime > 0:
        self.ctime = 0
    return False


configJsonPath = './json/rotation-motor/rotation-motor-test.json'  # default config
if len(sys.argv) > 1:
  configJsonPath = sys.argv[1]
print("load config file:", configJsonPath)
confDic = None
with open(configJsonPath, 'r') as f:
  confDic = json.load(f)

if confDic is None:
  print("load config error")
  sys.exit(1)

# modbusRtu timeout
modTimeout = confDic['modbusTimeout']
# motor slaveID
motorAddr = confDic['motorSlaveID']
# proximity sensor slaveID
proxiSenAddr = confDic['proxiSensorSlaveID']
# proximity sensor slot
proxiSenSlot = confDic['proxiSensorSlot']
# proximity sensor channel
proxiSenCh = confDic['proxiSensorChannel']
# 모터 주파수(속도)
freq = confDic['motorFrequency']
# 회전 칸 수 (한 바퀴 = 4 칸)
hitCnt = confDic['totalHitCount']
# 근접센서 Hit reverse (default Hit = True)
reverse = confDic['hitReverse']
# 중앙 정렬을 위한 대기시간
centerWaitSec = confDic['centerWaitSce']
# 최대 작동 제한 시간 (sec)
totalRunLimitSec = confDic['totalRunLimitSec']

# rtu inverter
rtu = ModbusClient(method='rtu', port='/dev/ttyUSB0', stopbits=1,
                   bytsize=8, parity='N', baudrate=9600, timeout=modTimeout, strict=False)

# rtu adam5
adam5 = ModbusClient(method='rtu', port='/dev/ttyS1', stopbits=1,
                     bytsize=8, parity='N', baudrate=9600, timeout=modTimeout, strict=False)

# 모터제어
vfd = modbus_VFD_LS(rtu, addr=motorAddr)
# 근접센서
proxiSen = AdamProxiSensor(adam5, addr=proxiSenAddr,
                           slot=proxiSenSlot, ch=proxiSenCh, reverse=reverse)


# 근접센서 StartOffset 설정
for i in range(5):
  offset = proxiSen.setStartOffset()
  print("sensorStartOffset=", offset)
  if offset is not None:
    break

# 초기화 (정지)
for i in range(5):
  status = vfd.motorOff()
  if status is None:
    continue
  if not vfd.on:
    print("INIT OFF")
    break

# 모터 주파수 설정
for i in range(5):
  refreq = vfd.setFreq(freq)
  print("FREQ=", freq)
  if freq == refreq:
    break

# 근접센서 초기상태 얻기
for i in range(5):
  initsw = proxiSen.getSenStatus()
  if initsw is not None:
    break

proxiSen.setInitValue(initsw)
print("sensor init status=", initsw)

# 모터 가동
for i in range(10):
  status = vfd.motorOn()
  if status is None:
    continue
  print("STATUS=", status)
  if vfd.on:
    print("MOTOR ON")
    break

stime = datetime.now()
ltime = datetime.now()
hitDiffList = []
lastHitDt = None
totalRunDt = None
while True:
  cnow = datetime.now()
  elsec = cnow - stime
  if elsec.seconds > totalRunLimitSec:
    break

  elsec = cnow - ltime
  if elsec.total_seconds() > 0.1:  # 100ms 마다 polling
    ltime = cnow
    # print(elsec.total_seconds())

    # 모터 이상 상태 확인
    tstatus = vfd.getTrip()
    if tstatus is not None:
      if(tstatus != 0):
        print("TRIP=", tstatus)
        break

    # 근접센서 칸 이동 확인
    if proxiSen.checkHit():
      diff = 0
      nowDt = datetime.now()
      if lastHitDt:
        diff = nowDt - lastHitDt  # hit 사이간 시간
      lastHitDt = datetime.now()
      print("HIT ---", proxiSen.count, diff)
      if diff != 0:
        hitDiffList.append(diff)
      if(proxiSen.count >= hitCnt+1):
        totalRunDt = nowDt - stime  # 총 회전 시간
        break

# 근접센서 상태가 확인되었으면 중앙 정렬을 위한 대기
if proxiSen.IsSet():
  time.sleep(centerWaitSec)

# 모터 정지
for i in range(5):
  status = vfd.motorOff()
  if status is None:
    continue
  #print("STATUS=", status)
  if not vfd.on:
    print("MOTOR OFF")
    break

# --- 결과 출력
hitDiffAvg = None
for dt in hitDiffList:
  if hitDiffAvg is None:
    hitDiffAvg = dt
  else:
    hitDiffAvg += dt
hitDiffAvg = hitDiffAvg/len(hitDiffList)

print("\n- 주파수="+str(freq)+" | 회전 칸 수="+str(hitCnt)+" | 초기 센서 상태="+str(initsw))
print("- hit 간격 평균:", hitDiffAvg)
print("- 한 바퀴 평균: ", hitDiffAvg*4)
print("- 총 회전 시간: ", totalRunDt)
