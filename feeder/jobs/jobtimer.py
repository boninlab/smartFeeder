from fdjob import FdJob
from datetime import datetime


class JobTimer(FdJob):
  def __init__(self, taskId, params):
    super().__init__(taskId, params)
    self.type = 'jobTimer'
    self.params = params.get('params', None)

  def setActive(self):
    super().setActive()
    #self.logger.info("timer %s" % (self.params))
    print("*timer:", self.params)
    self.started = datetime.now()

  def isDone(self):
    durationSec = (int(self.params['duration']['min'])
                   * 60) + int(self.params['duration']['sec'])
    diff = (datetime.now()-self.started).seconds
    if diff >= durationSec:
      self.setDone()
    return super().isDone()
