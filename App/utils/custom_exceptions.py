from ..logger import Logger

log = Logger.get(__name__)

class SessionException(Exception):
  def __init__(self, exceptions):
    self.exceptions = exceptions
  # def __str__(self):
