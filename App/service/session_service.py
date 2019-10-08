from time import sleep
import os
from datetime import datetime
from . import BaseService
from ..logger import Logger
from ..database import db, Profile, Session, SessionSetting, SessionSettings, AppSettings, ProfileSettings
from ..session import SessionMeta, SessionRepository
from ..session.session_submodule import start_session
from ..utils.process_utils import Executor

log = Logger.get(__name__)

executor = Executor()

class SessionService(BaseService):
  @staticmethod
  def init_app(app):
    # When app starts, restart sessions that:
    # - were running
    # - should run 24/7
    try:
      with app.app_context():
        all_sessions_to_run = SessionRepository.get_sessions_to_run_on_app_startup()
        # We don't want to overload the system upon start, throttle the start of the sessions
        # Every 2 sessions started sleep for few seconds
        i = 0
        for session in all_sessions_to_run:
          SessionService.start_session(session.id)
          if i % 2:
            sleep(3) # in seconds
          i = i + 1
    except Exception as exc:
      log.error(exc, exc_info=True)
  @classmethod
  def start_session(cls, session_id, workload_function=None):
    # We don't want to run same session twice
    if cls.is_session_running(session_id):
      return True
    try:
      session_meta = SessionMeta(session_id, workload_function)
      session_meta.run_forever = SessionRepository.should_session_run_forever(session_id)

      # DEBUG POINT
      #SessionRepository.populate_session_meta(session_meta)

      return executor.worker_start(worker_id=session_id, meta_data=session_meta, target_func=start_session, run_forever=session_meta.run_forever)
    except Exception as exc:
      log.error(exc, exc_info=True)
      return None
  @classmethod
  def is_session_running(cls, session_id):
    return executor.is_worker_running(session_id)
  @classmethod
  def stop_session(cls, session_id):
    if not cls.is_session_running(session_id):
      return True
    result = executor.worker_stop(session_id)
    # We have to update session ending datetime here because
    # it doesn't work from the submodule when the process is stopped manually
    if result:
      try:
        session = Session.query.filter(id=session_id).first()
        if session:
          session.end_datetime = datetime.now()
          db.session.add(session)
          db.session.commit()
      except Exception as exc:
        log.error(exc, exc_info=True)
    return result
  @classmethod
  def restart_session(cls, session_id):
    stop = cls.stop_session(session_id)
    start = cls.start_session(session_id)
    return stop and start
  @classmethod
  def multiple_sessions_action(cls, sessions, action):
    if not sessions:
      return True
    all_sessions_actioned = True
    for session in sessions:
      if action == 'start':
        action_done = cls.start_session(session.id)
      if action == 'stop':
        action_done = cls.stop_session(session.id)
      if action == 'restart':
        action_done = cls.restart_session(session.id)
      if not action_done:
        all_sessions_actioned = False
    return all_sessions_actioned
  @classmethod
  def stop_multiple_sessions(cls, sessions):
    return cls.multiple_sessions_action(sessions, 'stop')
  @classmethod
  def start_multiple_sessions(cls, sessions):
    return cls.multiple_sessions_action(sessions, 'start')
  @classmethod
  def restart_multiple_sessions(cls, sessions):
    return cls.multiple_sessions_action(sessions, 'restart')






