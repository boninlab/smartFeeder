#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
import sys

uaddr = 10
chLen = 8

rtu = ModbusClient(
    method="rtu",
    port="/dev/ttyS1",
    stopbits=1,
    bytsize=8,
    parity="N",
    baudrate=9600,
    timeout=0.03,
    strict=False,
)

slot = int(input("SLOT:"))
if slot < 2:
  chLen *= 2

for i in range(5):
  try:
    value = rtu.read_holding_registers(10020+(slot*2), 2, unit=uaddr)
    result = value.registers
    slotSt = result[0] - 1
    print("SLOT"+str(slot)+" START=", result[0], "END=", result[1])
    break
  except:
    print("read_holding_registers Error..")
    time.sleep(0.2)
    continue

while True:
  for i in range(5):
    try:
      value = rtu.read_coils(slotSt, chLen, unit=uaddr)
      #result = value.registers
      bits = value.bits
      pstr = ""
      for index, b in enumerate(bits):
        tstr = ""
        if index % 2 != 0:
          tstr = " "
        pstr += "%s:%s %s" % (str(index), str(b), str(tstr))
      print(pstr)

      break
    except:
      print("read_coils Error..")
      time.sleep(0.2)
      continue
  time.sleep(0.5)
