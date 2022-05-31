#!/usr/bin/python3
from fdtaskdetail import FdTaskDetail


class FeedTank(FdTaskDetail):
  def __init__(self, params):
    super().__init__(params)
    self.taskType = "feedTank"
    self.hopperNum = None
    self.tankNum = None
    self.feederFreq = 40
    self.blowerFreq = 40

  def prepareToStart(self):
    hopperNum = self.params['hopperNum']
    tankNum = self.params['tankNum']
    count = self.params['kg']
    # --- feedTank mod On
    # 수조 밸브 OPEN
    self.createJob('tankValve', params={
                   'devNum': tankNum, 'action': 'open'}, waitDevSignal=True)
    # blower 방향으로 설정
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'blower'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # blower ON
    self.createJob('blower', params={'devNum': 0, 'action': self.blowerFreq})
    # blower ON 대기
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 3}})
    # feeder ON
    self.createJob('feeder', params={
                   'devNum': hopperNum, 'action': {'value': self.feederFreq, 'count': count}}, waitDevSignal=True)

    # --- feedTank mod Off
    # feeder OFF
    self.createJob('feeder', params={
                   'devNum': hopperNum, 'action': {'value': 'off'}})
    # 먹이 공급기 OFF 대기(먹이가 수조까지 전달 대기)
    self.createJob('jobTimer', params={'duration': {'min': 0, 'sec': 10}})
    # blower OFF
    self.createJob('blower', params={'devNum': 0, 'action': 'off'})
    # water(default) 방향으로 설정
    self.createJob('startValve', params={
                   'devNum': 0, 'action': 'water'}, waitDevSignal=True)
    # 수조 밸브 CLOSE
    self.createJob('tankValve', params={
                   'devNum': tankNum, 'action': 'close'}, waitDevSignal=True)
    # 밸브 전환 대기
    self.createJob('jobTimer', params={'duration': {
                   'min': 0, 'sec': 10}}, finalJob=True)

    return self.jobs
