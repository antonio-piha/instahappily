#
#=====================================
#
# THIS FILE IS THE APP STARTING POINT
#
#=====================================
#
#
import sys

# For InstaPy imports
sys.path.append("..")

from flask import Flask, flash, redirect
from .create_app import create_app, ensure_app_dirs
from .logger import Logger

ensure_app_dirs()
Logger.ensure_log_file_exists()

# =========================================================

from . import frontend
from .nav import nav
from .database import init_database
from .settings import Settings
from . import templates_context
from . import on_exit
from . import service

log = Logger.get(__name__)
app = create_app(__name__)

# APP initialisation
try:
  init_database(app)
  templates_context.init_app(app)
  frontend.init_app(app)
  nav.init_app(app)
  service.init_app(app)
except Exception as exc:
  log.error(exc, exc_info=True)

# If everything else fails this will handle all Exceptions
@app.errorhandler(Exception)
def handle_exceptions(exc):
  flash('Unfortunately something bad happened and you got redirected to homepage. This error will be reported and fixed. Please try again what you were initially trying do to.', 'danger')
  log.warning(exc, exc_info=True)
  return redirect('/')

log.info('App started.')


