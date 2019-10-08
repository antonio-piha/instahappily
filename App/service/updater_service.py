import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
from . import BaseService
from ..logger import Logger
from ..settings import Settings, Environment
from ..database import AppSettings

log = Logger.get(__name__)

serial_key_hash = None

class UpdaterService(BaseService):
  @staticmethod
  def init_app(app):
    global serial_key_hash
    try:
      serial_key_settings = AppSettings.query.filter(key='serial_key_hash').first()
      if serial_key_settings:
        serial_key_hash = serial_key_settings.value
    except Exception as exc:
      log.error(exc, exc_info=True)
  @staticmethod
  def schedule_update_check():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=UpdaterService.check_for_update, trigger='interval', seconds=Settings.update_check_interval)
    scheduler.start()
  @staticmethod
  def check_for_update():
    data = {
      'protected': serial_key_hash
    }
    data = json.dumps(data)
    response = requests.post(Settings.update_service_check_version_url, data=data)


