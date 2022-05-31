#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class VibHopper(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "vibHopper"
    self.durationSec = (
        int(self.params['duration']['min'])*60) + int(self.params['duration']['sec'])
    self.freq = 40
    self.ledNum = 0

  def prepareToStart(self):
    hopperNum = self.params['hopperNum']
    self.ledNum += hopperNum
    # --- vibMotor mod On
    # LED ON
    self.createJob('led', params={'devNum': self.ledNum, 'action': 'on'})
    # 진동 모터 ON
    self.createJob('vibMotor', params={
                   'devNum': hopperNum, 'action': self.freq})

    # 설정된 duration만큼 대기
    self.createJob('jobTimer', params={'duration': {
                   'min': 0, 'sec': self.durationSec}})

    # --- vibMotor mod Off
    # 진동 모터 OFF
    self.createJob('vibMotor', params={'devNum': hopperNum, 'action': 'off'})
    # 진동 모터 OFF 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 3}})
    # LED OFF
    self.createJob(
        'led', params={'devNum': self.ledNum, 'action': 'off'}, finalJob=True)

    return self.jobs
