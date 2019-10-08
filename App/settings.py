""" Global variables """
import os
import logging
from sys import platform as p_os
from InstaPy.instapy import Settings as DefaultInstaPySettings
from ._version import __version__ as app_version

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_location_folder = os.path.join(base_dir, 'assets')
OS_ENV = 'windows' if p_os=='win32' else 'osx' if p_os=='darwin' else 'linux'

class Environment:
  # platform related
  is_windows = True if OS_ENV == 'windows' else False
  is_linux = True if OS_ENV == 'linux' else False
  is_mac = True if OS_ENV == 'osx' else False


class InstaPySettings:
  # INSTAPY Configs
  assets_location = os.path.join(assets_location_folder, 'InstaPy')
  log_location = os.path.join(assets_location, 'logs')
  database_location = os.path.join(assets_location, 'instapy.db')

  # Special files
  follower_num_txt_file = 'followerNum.txt'
  following_num_txt_file = 'followingNum.txt'

  # Chromedriver
  chromedriver_location = os.path.join(assets_location, DefaultInstaPySettings.specific_chromedriver)
  if not os.path.exists(chromedriver_location):
    chromedriver_location = os.path.join(assets_location, 'chromedriver')

class Settings:
  log_level = None

  #############################
  # version format= major.minor
  app_version = app_version
  #############################

  assets_location = os.path.join(assets_location_folder, 'App')
  log_file = os.path.join(assets_location, 'app.log')

  database_location = os.path.join(assets_location, 'database.db')
  migrations_location = os.path.join(base_dir, 'App', 'database', 'migrations')
  secret_key_location = os.path.join(assets_location, 'math.bin')

  # Needs to be uppercase
  SECRET_KEY = os.urandom(16)
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + database_location
  SQLALCHEMY_BINDS = {
    'instapy': 'sqlite:///' + InstaPySettings.database_location
  }
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  # DEBUG = False

  update_service_base_url = 'https://backoffice.instahappily.com'
  update_service_check_version_url = '{}/get-client-app-latest-version/client_os_type/{}'.format(update_service_base_url, OS_ENV)
  update_check_interval = 100000 # seconds

# set log level from environment
# Check this to not call it more than needed (once in best case)
# no need to check everytime module is imported elsewhere
if Settings.log_level is None:
  #######################################
  # default is ERROR
  # Because InstaPy and App produce alot of messages on level INFO
  #######################################
  log_level = logging.ERROR
  log_level_str = os.environ.get('LOG_LEVEL', None)
  if log_level_str:
    log_level = getattr(logging, log_level_str, log_level)
  Settings.log_level = log_level


# Override InstaPy defaults
# no need to override everytime module is imported elsewhere
if DefaultInstaPySettings.log_location != InstaPySettings.log_location:
  DefaultInstaPySettings.log_location = InstaPySettings.log_location
if DefaultInstaPySettings.database_location != InstaPySettings.database_location:
  DefaultInstaPySettings.database_location = InstaPySettings.database_location
if DefaultInstaPySettings.chromedriver_location != InstaPySettings.chromedriver_location:
  DefaultInstaPySettings.chromedriver_location = InstaPySettings.chromedriver_location


