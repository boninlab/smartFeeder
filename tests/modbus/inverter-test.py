#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from datetime import datetime
import time
import sys
import json


class modbus_VFD_LS:
  def __init__(self, rtu, addr, reverseOn=False):
    self.rtu = rtu
    self.addr = addr
    self.on = False
    self.reverseOn = reverseOn

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
    elif (result[0] & 4) != 0:  # 역방향 ON
      self.on = True
    return result[0]

  def setFreq(self, fval):
    self.rtu.write_register(0x0005-1, int(fval*100), unit=self.addr)
    return self.getFreq()

  def motorOn(self):
    drc = 2
    if self.reverseOn:  # 51(blower)역회전
      print("!!reverseOn")
      drc = 4
    self.rtu.write_register(0x0006-1, drc, unit=self.addr)  # 2: 정회전, 4:역회전
    return self.getStatus()

  def motorOff(self):
    self.rtu.write_register(0x0006-1, 1, unit=self.addr)
    return self.getStatus()


configJsonPath = './json/inverter/inverter-test.json'  # default config
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
# inverter slaveID
inverterAddr = confDic['inverterSlaveID']
print("inverterSlaveID:", inverterAddr)
# 모터 주파수(속도)
freq = confDic['inverterFrequency']
# 작동 시간 (sec)
runTimeSec = confDic['runTimeSec']
# reverseOn
reverseOn = False
if "reverseOn" in confDic:
  reverseOn = bool(confDic['reverseOn'])
  # rtu
rtu = ModbusClient(method='rtu', port='/dev/ttyUSB0', stopbits=1,
                   bytsize=8, parity='N', baudrate=9600, timeout=modTimeout, strict=False)
# 인버터
vfd = modbus_VFD_LS(rtu, addr=inverterAddr, reverseOn=reverseOn)

# 초기화 (정지)
for i in range(5):
  status = vfd.motorOff()
  if status is None:
    continue
  if not vfd.on:
    print("INIT OFF")
    break

# 주파수 설정
for i in range(5):
  refreq = vfd.setFreq(freq)
  print("FREQ=", refreq)
  if freq == refreq:
    break

# 가동
for i in range(10):
  status = vfd.motorOn()
  if status is None:
    continue
  print("STATUS=", status)
  if vfd.on:
    print("INVERTER ON")
    break

stime = datetime.now()
ltime = datetime.now()
totalRunDt = None
while True:
  cnow = datetime.now()
  elsec = cnow - stime
  if elsec.seconds > runTimeSec:
    break

  elsec = cnow - ltime
  if elsec.total_seconds() > 0.1:  # 100ms 마다 polling
    ltime = cnow
    # print(elsec.total_seconds())

    # 이상 상태 확인
    tstatus = vfd.getTrip()
    if tstatus is not None:
      if(tstatus != 0):
        print("TRIP=", tstatus)
        break

# 정지
for i in range(5):
  status = vfd.motorOff()
  if status is None:
    continue
  #print("STATUS=", status)
  if not vfd.on:
    print("INVERTER OFF")
    totalRunDt = datetime.now() - stime
    break

# --- 결과 출력

print("\n- 주파수="+str(freq))
print("- 총 작동 시간: ", totalRunDt)
