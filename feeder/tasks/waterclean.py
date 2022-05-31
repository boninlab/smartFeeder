#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class WaterClean(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "waterClean"
    self.durationSec = (
        int(self.params['duration']['min'])*60) + int(self.params['duration']['sec'])
    self.ledNum = 2

  def prepareToStart(self):
    # --- waterClean mod On
    # LED ON
    self.createJob('led', params={'devNum': self.ledNum, 'action': 'on'})
    # water 방향으로 설정
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'water'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # 입수 밸브 OPEN
    self.createJob('waterValve', params={
                   'devNum': 0, 'action': 'open'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})

    # 설정된 duration만큼 대기
    self.createJob('jobTimer', params={'duration': {
                   'min': 0, 'sec': self.durationSec}})

    # --- waterClean mod Off
    # 입수 밸브 CLOSE
    self.createJob('waterValve', params={
                   'devNum': 0, 'action': 'close'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # LED OFF
    self.createJob(
        'led', params={'devNum': self.ledNum, 'action': 'off'}, finalJob=True)
    return self.jobs
