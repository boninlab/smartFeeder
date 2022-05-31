#!/usr/bin/python3
import time
import threading
from configparser import ConfigParser
from queue import Queue
from fdtask import FdTask
from fdrecv import FdReceiver
import fdtaskdetail
from fddevice import FdDevice
from fdconn import FdConnection
from devcommunicator import DevCommunicator
from actuators import *
from devices import *
from fdlogging import FdLogger
from apiflask import runApiFlask

g_logger = FdLogger()
mainTask = FdTask()


def task(q, devResponse):
  global g_logger, mainTask
  recv = FdReceiver()
  recv.start()
  mainTask.logger = g_logger
  jobQ = Queue(maxsize=512)
  currJob = None

  while True:
    newJobs, interrupt = mainTask.loop()
    if newJobs:
      if interrupt == True:  # 최우선 job 추가
        newJobs.reverse()
      for job in newJobs:
        if interrupt == True:
          jobQ.queue.insert(0, job)
        else:
          jobQ.put(job)
    if currJob == None:
      if jobQ.qsize() > 0:
        currJob = jobQ.get()
        # print("active", currJob)
        currJob.setActive()
    else:
      if mainTask.getTaskStatus(currJob.taskId) != 2:  # pause 상태
        while currJob.hasDevActs():
          q.put(currJob.getDevAct())
        if len(devResponse) > 0:  # device로 부터 받은 msg
          res = devResponse.pop()
          # print(currJob.type, res)
          if currJob.type in res:
            if res[currJob.type] == 200:
              currJob.waitDevSignal = False
            elif res[currJob.type] == 500:  # 오류
              g_logger.error("JOB", "report %s %s" % (currJob, res['msg']))
              print("\n!!ERROR:", "report %s %s" % (currJob, res['msg']))
              mainTask.pauseTask(currJob.taskId)
              jobQ.queue.insert(0, currJob)  # pause된 job 다시 jobQ 넣어두기
              currJob = None
              continue
        if currJob.isDone():
          # print("done", currJob)
          if currJob.finalJob:
            mainTask.doneTask(currJob.taskId)
          currJob = None
    while recv.hasMessage():
      msg = recv.popMessage()
      params = None

      if 'system' in msg:
        msg = msg['system']
        if 'cmd' in msg:  # system cmd
          msg = msg['cmd']
          params = msg['params']
          if params['cmd'] == 'reset':
            jobQ.queue.clear()
            currJob = None
            mainTask.initState()

      elif 'task' in msg:
        msg = msg['task']
        if 'cmd' in msg:  # Task cmd
          msg = msg['cmd']
          params = msg['params']
          if params['cmd'] == 'pause':
            if currJob != None:
              mainTask.pauseTask(currJob.taskId)
          elif params['cmd'] == 'pause':
            if currJob != None:
              mainTask.resumeTask(currJob.taskId)
              q.put({"warnLight0": "off"})
        elif 'add' in msg:  # add Task
          msg = msg['add']
          params = msg['params']
          mainTask.addTask(msg['taskType'], params=params)

      elif 'job' in msg:
        msg = msg['job']
        if 'add' in msg:
          msg = msg['add']
          params = msg['params']
          job = fdtaskdetail.getJobObjByType(
              msg['jobType'], None, params=params)
          job.logger = g_logger
          jobQ.put(job)

    time.sleep(0.01)


def device(q, devResponse):
  etcDir = '/etc/smart-feeder'
  devices = []
  actuators = []
  conns = []

  def lookupObjWithKey(type, kind):
    objList = []
    if kind == 'connection':
      objList = conns
    elif kind == 'actuator':
      objList = actuators
    elif kind == 'device':
      objList = devices
    for obj in objList:
      if obj.type == type:
        return obj
    return None

  def loadConfigFromIni(filePath, kind):
    config = ConfigParser()
    config.read(etcDir+"/"+filePath)
    for section in config.sections():
      if kind == 'connection':
        conns.append(FdConnection(config[section]))
      elif kind == 'actuator':
        if config[section]['type'] == 'relay_adam5':
          actuator = RelayAdam5(config[section])
        elif config[section]['type'] == 'switch_adam5':
          actuator = SwitchAdam5(config[section])
        elif config[section]['type'] == 'lsSv004ig5a_1':
          actuator = LsSv004ig5a_1(config[section])
        elif config[section]['type'] == 'onOffRelay':
          actuator = OnOffRelay(config[section])
        else:
          print("actuator class not found", config[section]['type'])
          break
        conn = lookupObjWithKey(config[section]['connection'], 'connection')
        if conn:
          actuator.conn = conn
          actuators.append(actuator)
        if config[section]['useDevice'] == 'true':
          actuator.actuator = actuator
          devices.append(actuator)
      elif kind == 'device':
        if config[section]['type'] == 'onoffValve':
          dev = OnoffValve(config[section])
        elif config[section]['type'] == 'RotationMotor':
          dev = RotationMotor(config[section])
        elif config[section]['type'] == 'InverterDev':
          dev = InverterDev(config[section])
        elif config[section]['type'] == 'onoffDevice':
          dev = OnoffDevice(config[section])
        else:
          print("device class not found", config[section]['type'])
          break
        actuatorSplit = config[section]['actuators'].split(',')
        actuator = lookupObjWithKey(actuatorSplit[0], 'actuator')
        subActuators = []
        if len(actuatorSplit) > 1:
          for a in actuatorSplit[1:]:
            reAct = lookupObjWithKey(a, 'actuator')
            if reAct:
              subActuators.append(reAct)
        if actuator:
          dev.actuator = actuator
        if len(subActuators) > 0:
          dev.subActuators = subActuators
        dev.logger = g_logger
        devices.append(dev)

  loadConfigFromIni('connections.ini', 'connection')
  loadConfigFromIni('actuators.ini', 'actuator')
  loadConfigFromIni('devices.ini', 'device')

  devCmnct = DevCommunicator()
  devCmnct.logger = g_logger
  devCmnct.start()
  while True:
    while len(q.queue) > 0:  # task에서 받은 action
      actDic = q.get()

      print("action:", actDic)
      # actDic: {'s0': 'water'}
      devId = next(iter(actDic))
      dev = lookupObjWithKey(devId, 'device')
      if 'waitDevSignal' in actDic:
        dev.waitDevSignal = actDic['waitDevSignal']
      if dev is None:
        print("Error! not found", devId)
        continue
      dev.command(actDic[devId])
    for dev in devices:
      devState = 0
      if dev.waitDevSignal == True:
        if len(dev.signalToTask) > 0:
          sig = dev.signalToTask.pop()
          # print("append", sig)
          devResponse.append(sig)  # Task로 보낼 신호
          dev.waitDevSignal = False
      dev.checkAction()  # dev에게 Action을 생성할 수 있는 턴을 제공
      if dev.hasAction():
        devState = 1
      if devState > 0:
        devCmnct.addActQueue(dev)

    time.sleep(0.001)


actQ = Queue(maxsize=512)
devResponse = []  # dev 정보 taskT에 전달

taskT = threading.Thread(target=task, args=(actQ, devResponse))
deviceT = threading.Thread(target=device, args=(actQ, devResponse))
apiFlaskT = threading.Thread(target=runApiFlask, args=(mainTask,))

taskT.start()
deviceT.start()
apiFlaskT.start()
