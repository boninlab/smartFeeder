from fdjob import FdJob


class JobDevice(FdJob):
  def __init__(self, jobType, taskId, params):
    super().__init__(taskId, params)
    self.params = params.get('params', None)
    self.waitDevSignal = params.get('waitDevSignal', None)
    self.type = jobType+str(self.params['devNum'])

  def setActive(self):
    act = {self.type: self.params['action']}
    if self.waitDevSignal == True:
      act.update({'waitDevSignal': True})
    self.devAct(act)
    super().setActive()

  def isDone(self):
    if self.waitDevSignal != True:  # dev 작업 대기(true면 기다림)
      self.setDone()
      return super().isDone()
