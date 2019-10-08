from ..logger import Logger

log = Logger.get(__name__)

class SessionMeta:
  def __init__(self, session_id = None, workload_function = None):
    self.session_id = session_id
    self.session = None
    self.settings = None
    self.session_settings = None
    self.profile_settings = None
    self.proxy = None
    self.app_settings = None
    self.username = None
    self.passwords = {
      'profile': '',
      'proxy': '',
    }
    self.logger_filter = None
    self.run_forever = None
    self.workload_function = workload_function
  def set_from_previous(self, session_meta):
    self.session_id = session_meta.session_id
    self.workload_function = session_meta.workload_function
    self.run_forever = session_meta.run_forever
    return self
