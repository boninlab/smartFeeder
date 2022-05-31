#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
import sys

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

if len(sys.argv) > 1:
  try:
    ch = int(sys.argv[1])
    value = sys.argv[2]
    print(ch, value)
    if value == 'on':
      value = True
    else:
      value = False
    rtu.write_coil(ch, value, unit=101)
  except Exception as ex:
    print(ex)
else:
  print('write ex) ./cmd_relay.py 5 on # 5번 채널 on / off')

while True:
  try:
    value = rtu.read_coils(0x0000, 8, unit=101)
    out = 0
    bits = value.bits
    pstr = ""
    for index, b in enumerate(bits):
      pstr += "%s:%s " % (str(index), str(b))
    print(pstr)
    for bit in bits[0:8]:
      out = (out << 1) | bit
      strdic = hex(out)
  except Exception as ex:
    print(ex)
    continue
  time.sleep(0.5)
