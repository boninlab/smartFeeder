#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
import sys
import json

uaddr = 10
chLen = 8

rtu = ModbusClient(
    method="rtu",
    port="/dev/ttyS1",
    stopbits=1,
    bytsize=8,
    parity="N",
    baudrate=9600,
    timeout=1,
    strict=False,
)

configJsonPath = './json/relay-mode/mode-write-test.json'  # default config
if len(sys.argv) > 1:
  configJsonPath = sys.argv[1]
print("load config file:", configJsonPath)
confList = None
with open(configJsonPath, 'r') as f:
  confList = json.load(f)

if confList is None:
  print("load config error")
  sys.exit(1)

for mode in confList:
  print("\nWRITE MODE:", mode)
  slot = mode['slot']
  chs = mode['ch']
  writeList = [False, False, False, False, False, False, False, False]
  slotSt = None
  for i in range(5):
    try:
      value = rtu.read_holding_registers(10020+(slot*2), 2, unit=uaddr)
      result = value.registers
      slotSt = result[0] - 1
      break
    except:
      print("read_holding_registers Error..")
      time.sleep(0.2)
      continue
  for ch in chs:
    writeList[ch] = True
  for i in range(5):
    try:
      rtu.write_coils(slotSt, writeList, unit=uaddr)
      break
    except:
      print("write_coils Error..")
      time.sleep(0.2)
      continue
  for i in range(5):
    try:
      value = rtu.read_coils(slotSt, chLen, unit=uaddr)
      print(value.bits)
      break
    except:
      print("read_coils Error..")
      time.sleep(0.2)
      continue
