#!/usr/bin/python3
import threading
import redis
from datetime import datetime
from queue import Queue


class DevCommunicator(threading.Thread):
  logger = None

  def __init__(self):
    threading.Thread.__init__(self)
    self.q = Queue(maxsize=512)
    self.rd = redis.StrictRedis(
        host='localhost', port=6379, charset="utf-8", decode_responses=True)

  def addActQueue(self, fddev):
    if fddev not in self.q.queue:
      self.q.put(fddev)

  def run(self):
    while True:
      dev = self.q.get()  # 액션이 필요한 디바이스 FdDevice
      actuator = dev.actuator
      conn = actuator.conn
      act = dev.getAction()
      if act is None:
        continue
      #print("ACT:", dev.type, dev.value, act)
      value = None
      if act['atype'] == 'modbus':
        rtu = conn.conn
        try:
          if act['func'] == 3:
            value = rtu.read_holding_registers(
                act['offset'], act['length'], unit=act['slaveid'])
            if not hasattr(value, 'registers'):
              value = None
              raise Exception('read_holding_registers error')
          elif act['func'] == 1:
            value = rtu.read_coils(
                act['offset'], act['length'], unit=act['slaveid'])
            if not hasattr(value, 'bits'):
              value = None
              raise Exception('read_coils error')
          elif act['func'] == 5:
            rtu.write_coil(act['offset'], act['value'], unit=act['slaveid'])
          elif act['func'] == 6:
            rtu.write_register(
                act['offset'], act['value'], unit=act['slaveid'])
        except:
          if dev.lastRetry < 5:
            dev.lastRetry += 1
            self.addActQueue(dev)
          else:
            msg = "bus connection failure"
            if dev.lastRetry < 6:
              print(dev.type+":", msg)
              self.logger.error(
                  "SYSTEM", "report %s (-1,-1,-1) %s" % (dev.type, msg))
              dev.lastRetry += 1

      elif act['atype'] == 'actuatorValue':  # actuator value에서 가져옴
        if 'actuator' in act:
          actuator = act['actuator']
        if actuator.value:
          value = actuator.value
      """if conn.mqtt:
        topic = conn.mqttRootTopic+'/'+actuator.mqttTopic+'/'+dev.type
        value = str(act)
        # print("- mqttPub:", topic, value)
        conn.mqtt.client.publish(topic, value, 0, True)"""
      if value is not None:
        dev.parse(act, value)
        if dev.value != None:
          val = dev.value
          if isinstance(val, list):
            out = 0
            for bit in val:
              out = (out << 1) | bit
            val = hex(out)
          self.rd.set('status/'+str(dev.type)+'/value', str(val))
          self.rd.set('status/'+str(dev.type)+'/lasttime', str(datetime.now()))
        if dev.lastRetry > 5:
          msg = "bus reconnected"
          self.logger.info(
              "SYSTEM", "report %s (-1,-1,-1) %s" % (dev.type, msg))
        dev.lastRetry = 0
