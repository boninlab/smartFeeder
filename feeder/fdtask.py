#!/usr/bin/python3
from datetime import datetime
from tasks import *
from collections import OrderedDict
import time


class FdTask:
  def __init__(self):
    self.tasks = OrderedDict()
    self.seqId = 0
    self.logger = None

  def loop(self):
    jobs = None
    if len(self.tasks) == 0:
      return None, None
    taskId = next(iter(self.tasks))
    task = self.tasks[taskId]
    if task.startTS > time.time():  # 시작 시간 대기
      return None, None
    if task.state == 0:  # ready
      task.state = 1
      jobs = task.prepareToStart()
      self.logger.info("TASK", "start {task}".format(task=task))
      print("--start {task}".format(task=task))
    elif task.state == 1:  # running
      pass
    elif task.state == 99:  # closed
      self.logger.info("TASK", "finish {task}".format(task=task))
      print("--finish", task, "\n")
      del(self.tasks[taskId])
    elif task.state == 2:  # pause
      return None, None

    if jobs:
      if task.interrupt == True:
        return jobs, True
      return jobs, False
    return None, None

  def addTask(self, taskType, interrupt=False, **params):
    taskId = datetime.now().strftime("%d%H%M_") + str(self.seqId)
    self.seqId += 1
    if taskType == "initState":
      task = InitState(params)
    elif taskType == "blowerClean":
      task = BlowerClean(params)
    elif taskType == "waterClean":
      task = WaterClean(params)
    elif taskType == "feedTank":
      task = FeedTank(params)
    elif taskType == "vibHopper":
      task = VibHopper(params)
    elif taskType == "pauseTask":
      task = PauseTask(params)
    else:
      return None
    task.logger = self.logger
    task.taskId = taskId
    re = task.setStartTime()
    if re == False:
      return None
    self.tasks[taskId] = task
    self.tasks = OrderedDict(sorted(
        self.tasks.items(), key=lambda x: x[1].startTS, reverse=False))  # 시간 순서로 정렬
    if interrupt == True:
      self.tasks.move_to_end(taskId, last=False)  # 맨 앞으로 이동
      self.tasks[taskId].interrupt = True
    self.logger.info("TASK", "add task {task}".format(task=task))
    print("***** add task:", task.taskType)
    return taskId

  def getTaskById(self, taskId):
    for id, task in self.tasks.items():
      if id == taskId:
        return task
    return None

  def doneTask(self, taskId):
    task = self.getTaskById(taskId)
    if task:
      task.state = 99

  def initState(self):
    self.tasks = OrderedDict()
    self.addTask("initState", params={}, interrupt=True)

  def pauseTask(self, taskId):
    task = self.getTaskById(taskId)
    if task:
      task.state = 2  # 현재 실행중인 task pause
      self.logger.info("TASK", "pause {task}".format(task=task))
      print("--pause {task}".format(task=task))
    self.addTask("pauseTask", params={'action': 'pause'}, interrupt=True)

  def resumeTask(self, taskId):
    task = self.getTaskById(taskId)
    if task:
      task.state = 1
      self.logger.info("TASK", "resume {task}".format(task=task))
      print("--resume {task}".format(task=task))

  def getTaskStatus(self, taskId):
    task = self.getTaskById(taskId)
    if task:
      return task.state
    return None
