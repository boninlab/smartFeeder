#!/usr/bin/python3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
rtu = ModbusClient(method='rtu', port='/dev/ttyS1', stopbits=1,
                   bytsize=8, parity='N', baudrate=9600, timeout=1, strict=False)

while True:
  try:
    # WaterRate
    value = rtu.read_input_registers(0x03EB, 2, unit=3)
    result = value.registers
    decoder = BinaryPayloadDecoder.fromRegisters(
        result[0:2], byteorder=Endian.Big, wordorder=Endian.Little)
    strval = "%d" % decoder.decode_32bit_uint()
    print('wr:', strval)
  except Exception as ex:
    continue
  time.sleep(0.2)
