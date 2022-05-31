#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
import sys
rtu = ModbusClient(method='rtu', port='/dev/ttyS1', stopbits=1,
                   bytsize=8, parity='N', baudrate=9600, timeout=1, strict=False)

if len(sys.argv) > 1:
  rtu.write_registers(0x0000, int(sys.argv[1]), unit=0)

value = rtu.read_holding_registers(0x0000, 1, unit=0)
slaveID = int(value.registers[0])
print('SlaveID:', slaveID)

while True:
  try:
    value = rtu.read_coils(0x0000, 8, unit=slaveID)
    out = 0
    bits = value.bits
    # print(bits)
    pstr = ""
    for index, b in enumerate(bits):
      pstr += "%s:%s " % (str(index), str(b))
    print(pstr)
    for bit in bits[0:8]:
      out = (out << 1) | bit
      strdic = hex(out)
    break
  except Exception as ex:
    time.sleep(0.1)
    continue
