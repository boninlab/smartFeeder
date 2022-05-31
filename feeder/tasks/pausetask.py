#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class PauseTask(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "pauseTask"

  def prepareToStart(self):
    self.createJob('feeder', params={
                   'devNum': 0, 'action': {'value': 'off'}})
    self.createJob('feeder', params={
                   'devNum': 1, 'action': {'value': 'off'}})
    self.createJob('vibMotor', params={'devNum': 0, 'action': 'off'})
    self.createJob('vibMotor', params={'devNum': 1, 'action': 'off'})
    self.createJob('blower', params={'devNum': 0, 'action': 'off'})
    self.createJob('warnLight', params={
                   'devNum': 0, 'action': 'on'}, finalJob=True)

    return self.jobs
