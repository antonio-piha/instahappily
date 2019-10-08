import os
from flask import Flask, flash
from .settings import assets_location_folder, Settings, InstaPySettings
from .logger import Logger

# Can't get logger instance here since it hasn't been initialised yet

# APP creation
def create_app(name=''):
  log = Logger.get(__name__)
  ensure_app_dirs()
  app = None
  try:
    app = Flask(name)
    Logger.init(app)
    app.config.from_object(Settings)
  except Exception as exc:
    app = None
    log.error(exc, exc_info=True)
  return app


def ensure_app_dirs():
  # Make sure all the folders exists
  # This should be covered with installation but it is good to double check
  directories = [
    assets_location_folder,
    Settings.assets_location,
    InstaPySettings.assets_location
  ]
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)

