#!/usr/bin/python3
from jobs import *
from datetime import datetime

g_jobseqId = 0


class FdJob:
  def __init__(self, taskId, params):
    global g_jobseqId
    self.logger = None
    self.taskId = taskId
    self.jobId = g_jobseqId
    self.finalJob = False
    self.params = params
    if bool(params.get('finalJob', False)):
      self.finalJob = True
    g_jobseqId += 1
    self.state = 0
    self.devActs = []

  def __str__(self):
    tid = self.taskId
    if tid == None:
      tid = -1
    return ("{type} ({jobid},{taskid},{state})".format(type=self.type, jobid=self.jobId, taskid=tid, state=self.state))

  def setActive(self):
    self.logger.info("JOB", "action %s %s" % (self, self.params))
    self.state = 1

  def setDone(self):
    self.state = 99

  def isDone(self):
    if self.state == 99:
      return True
    return False

  def hasDevActs(self):
    if len(self.devActs) > 0:
      return True
    else:
      return False

  def getDevAct(self):
    return self.devActs.pop()

  def devAct(self, actDic):
    self.devActs.append(actDic)
