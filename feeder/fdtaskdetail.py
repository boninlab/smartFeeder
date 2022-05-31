#!/usr/bin/python3
from jobs import *
from datetime import datetime


def getJobObjByType(jobType, taskId, **params):
  if jobType == "jobTimer":
    job = JobTimer(taskId, params)
  else:
    job = JobDevice(jobType, taskId, params)
  return job


class FdTaskDetail:
  def __init__(self, params):
    self.taskId = None
    self.logger = None
    self.state = 0
    self.jobs = []
    self.params = params.get('params', None)
    self.startTS = 1000
    self.interrupt = False

  def __str__(self):
    return ("{tasktype} ({taskid},{state})".format(tasktype=self.taskType, taskid=self.taskId, state=self.state))

  def setStartTime(self):
    if 'startDateTime' in self.params:
      try:
        self.startTS = datetime.timestamp(datetime.strptime(
            self.params['startDateTime'], '%Y-%m-%d %H:%M:%S'))
      except:
        self.logger.error("SYSTEM", "add task input type(startDateTime) error")
        return False
    return True

  def createJob(self, jobType, **params):
    job = getJobObjByType(jobType, self.taskId, **params)
    job.logger = self.logger
    self.jobs.append(job)
