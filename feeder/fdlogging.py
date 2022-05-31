import logging.handlers


class FdLogger:
  def __init__(self):
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s')
    self.fHandler = logging.handlers.TimedRotatingFileHandler(
        filename='/var/log/smart-feeder/feederlog', when='midnight', interval=1, backupCount=30, encoding='utf-8')
    self.fHandler.suffix = '%Y%m%d'
    self.fHandler.setFormatter(formatter)
    self.logger.addHandler(self.fHandler)

  def setFormatter(self, logType):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s '+logType+': %(message)s')
    self.fHandler.setFormatter(formatter)

  def info(self, logType, msg):
    self.setFormatter(logType)
    self.logger.info(msg)

  def error(self, logType, msg):
    self.setFormatter(logType)
    self.logger.error(msg)
