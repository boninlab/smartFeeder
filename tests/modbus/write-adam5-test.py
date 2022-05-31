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
    timeout=1,
    strict=False,
)

if len(sys.argv) < 3:
  print("Error (.py {Slot} {Channel} {on/off})\n ex) \n\
./adamWrite_test.py 1 0 on\n./adamWrite_test.py 1 all off\n")
  sys.exit(1)

slot = int(sys.argv[1])
if slot < 2:
  chLen *= 2

inVal = None
if sys.argv[2] == 'all':
  ch = 99
else:
  ch = int(sys.argv[2])

if len(sys.argv) > 3:
  inVal = sys.argv[3]

val = False
if inVal == 'on':
  val = True

print(slot, ch, val, chLen)

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

if ch == 99:
  rtu.write_coils(slotSt, [val] * chLen, unit=uaddr)
else:
  rtu.write_coil(slotSt+ch, val, unit=uaddr)

time.sleep(0.2)

for i in range(5):
  try:
    value = rtu.read_coils(slotSt, chLen, unit=uaddr)
    #result = value.registers
    print(value.bits)
    break
  except:
    print("read_coils Error..")
    time.sleep(0.2)
    continue
