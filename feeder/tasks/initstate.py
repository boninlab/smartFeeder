#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class InitState(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "initState"

  def prepareToStart(self):
    self.createJob('waterValve', params={
                   'devNum': 0, 'action': 'close'})
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'water'})
    self.createJob('feeder', params={
                   'devNum': 0, 'action': {'value': 'off'}})
    self.createJob('feeder', params={
                   'devNum': 1, 'action': {'value': 'off'}})
    self.createJob('vibMotor', params={'devNum': 0, 'action': 'off'})
    self.createJob('vibMotor', params={'devNum': 1, 'action': 'off'})
    self.createJob('blower', params={'devNum': 0, 'action': 'off'})
    for i in range(1, 12):
      self.createJob('tankValve', params={
                     'devNum': i, 'action': 'close'})
    for i in range(0, 3):
      self.createJob('led', params={'devNum': i, 'action': 'off'})
    self.createJob('warnLight', params={'devNum': 0, 'action': 'off'})
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {
                   'min': 0, 'sec': 15}}, finalJob=True)

    return self.jobs
