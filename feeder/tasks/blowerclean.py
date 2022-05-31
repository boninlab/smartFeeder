#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class BlowerClean(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "blowerClean"
    self.durationSec = (
        int(self.params['duration']['min'])*60) + int(self.params['duration']['sec'])
    self.freq = 60
    self.ledNum = 3

  def prepareToStart(self):
    # --- blowerClean mod On
    # LED ON
    self.createJob('led', params={'devNum': self.ledNum, 'action': 'on'})
    # blower 방향으로 설정
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'blower'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # blower ON
    self.createJob('blower', params={'devNum': 0, 'action': self.freq})

    # 설정된 duration만큼 대기
    self.createJob('jobTimer', params={'duration': {
                   'min': 0, 'sec': self.durationSec}})

    # --- blowerClean mod Off
    # blower OFF
    self.createJob('blower', params={'devNum': 0, 'action': 'off'})
    # water(default) 방향으로 설정
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'water'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # LED OFF
    self.createJob(
        'led', params={'devNum': self.ledNum, 'action': 'off'}, finalJob=True)
    return self.jobs
