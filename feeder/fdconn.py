#!/usr/bin/python3
from mqtthelper import MqttObj
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

import os
import serial
import json
import ast
import serial.tools.list_ports


def getPortPath(connParams):
  portType = connParams[0]
  portId = connParams[1]
  if portType == 'usb':
    cmd = ("dmesg | grep 'usb "+portId+"' | grep 'attached to ttyUSB'")
  elif portType == 'com':
    cmd = ("dmesg | grep '"+portId+":' | grep 'is a'")
  else:
    return False
  fname = os.path.expanduser("~")+"/.last_portInfo"
  stream = os.popen(cmd)
  lines = stream.read().split('\n')
  try:
    with open(fname, "r") as f:
      contents = f.read()
      pdict = ast.literal_eval(contents)
  except:
    pdict = {}
  if len(lines) < 2:  # dmesg에서 못 찾은 경우
    if portId in pdict:
      ppath = pdict[portId]
    else:  # 파일에서도 못 찾은 경우
      print("Failed to set port..", portId)
      syslog(LOG_ERR, "Failed to set port.. "+portId)
      return False
  else:
    if portType == 'usb':
      ppath = "/dev/"+lines[-2].split(' ')[-1]
    elif portType == 'com':
      ppath = "/dev/"+lines[-2].split(' ')[6]
    else:
      return False
  pdict.update({portId: ppath})
  ports = serial.tools.list_ports.comports(include_links=False)
  find = 0
  if ports:
    for port in ports:
      if port.device == ppath:
        find = 1
        break
  if find == 0:
    print(ppath+" not found.")
    syslog(LOG_ERR, ppath+" not found.")
    return False

  with open(fname, "w") as f:
    f.write(json.dumps(pdict))  # 포트 경로 저장

  return ppath


class FdConnection:
  def __init__(self, connInfo):
    self.type = connInfo.name  # section name
    self.conn = None
    self.connType = connInfo['type']
    self.connParam = connInfo['connParameter'].split(',')
    self.mqttRootTopic = None
    self.mqtt = None

    if 'mqttPublishInfo' in connInfo:
      mqttPublishInfo = connInfo['mqttPublishInfo'].split(',')
      self.mqttRootTopic = mqttPublishInfo[1]
      broker = mqttPublishInfo[0].split(':')
      self.mqtt = MqttObj(broker[0], int(broker[1]), self.type)
      self.mqtt.start()

    portPath = getPortPath(self.connParam)
    baudrate = int(self.connParam[2])
    parity = self.connParam[3]
    bytesize = int(self.connParam[4])
    stopbits = int(self.connParam[5])
    timeout = float(self.connParam[6])
    strict = bool(self.connParam[7])

    if self.connType == 'modbus485':
      self.conn = ModbusClient(method='rtu', port=portPath, stopbits=stopbits,
                               bytsize=bytesize, parity=parity, baudrate=baudrate, timeout=timeout, strict=strict)
