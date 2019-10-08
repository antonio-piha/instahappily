import os
import logging
from flask.logging import default_handler
from logging.config import dictConfig
from .settings import Settings

class AppLoggerFilter(logging.Filter):
  def __init__(self):
    self._throttling_errors = set()
  def filter(self, record):
    if not record or record is None:
      return True
    if record.levelname != 'ERROR':
      return True

    log_representation = record.filename + record.name + record.getMessage()
    if log_representation in self._throttling_errors:
      return False
    self._throttling_errors.add(log_representation)

    # TODO: Implement sending notifications to server

    return True

class SessionLoggerFilter(logging.Filter):
  def filter(self, record):

    return True

class Logger():
  @classmethod
  def init(cls, app):
    app.logger.removeHandler(default_handler)
    cls.adjust_logger(app.logger)
  @classmethod
  def adjust_logger(cls, logger):
    try:
      file_handler = cls.get_file_handler()
      filter = AppLoggerFilter()
      # attach to logger
      logger.addHandler(file_handler)
      logger.addFilter(filter)
      logger.setLevel(Settings.log_level)
    except Exception as exc:
      pass
  @classmethod
  def get(cls, name):
    logger = logging.getLogger(name)
    cls.adjust_logger(logger)
    return logger
  @classmethod
  def get_file_handler(cls):
    formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(name)s: %(message)s')
    file_handler = logging.FileHandler(Settings.log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(Settings.log_level)
    return file_handler
  @classmethod
  def ensure_log_file_exists(cls):
    log_file = Settings.log_file
    if not os.path.isfile(log_file):
      with open(log_file, "a"):
        pass


# SessionLoggerFilter record example:
######################################
# <LogRecord: taninuyar, 20, D:\PROJEKTI\INSTA\SOURCE\InstaPy\instapy\util.py, 872, "Logged in successfully!">
# args:()
# created:1540667328.7092178
# exc_info:None
# exc_text:None
# filename:'util.py'
# funcName:'highlight_print'
# levelname:'INFO'
# levelno:20
# lineno:872
# module:'util'
# msecs:709.2177867889404
# msg:'Logged in successfully!'
# name:'taninuyar'
# pathname:'D:\\PROJEKTI\\INSTA\\SOURCE\\InstaPy\\instapy\\util.py'
# process:7252
# processName:'MainProcess'
# relativeCreated:73716.46571159363
# stack_info:None
# thread:9376
# threadName:'Thread-26'
# username:'taninuyar'
######################################
