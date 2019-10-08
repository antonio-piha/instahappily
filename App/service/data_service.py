import json
from . import BaseService
from ..logger import Logger
from ..database import db, AppSetting, AppSettings, ProfileSetting, SessionSetting
from ..security import EncryptionUnit

log = Logger.get(__name__)

class DataService(BaseService):
  @staticmethod
  def from_model_value_to_view_model_value(model_value, model_type=None):
    value = None
    try:
      # general case
      value = model_value
      # specific cases
      if model_type == 'boolean':
        if value is not None:
          value = value.upper() == 'TRUE'
        else:
          value = False
      elif model_type == 'number':
        if value is not None:
          value = int(float(value)) # Safer: float -> int
        else:
          value = 0
      elif model_type == 'decimal':
        if value is not None:
          value = float(value)
        else:
          value = 0
      elif model_type == 'list':
        if value is not None:
          value = json.loads(value)
        else:
          value = []
    except Exception as exc:
      log.error('Value = {}'. format(value), exc_info=True)
      value = None
    return value
  @staticmethod
  def from_setting_model_value_to_setting_view_model_value(model_value, model_type):
    view_model_value = None
    if model_value and model_type:
      view_model_value = DataService.from_model_value_to_view_model_value(
        model_value=model_value,
        model_type=model_type
      )
    return view_model_value
  @staticmethod
  def from_view_model_value_to_model_value(view_model_value, view_model_type):
    model_value = None
    try:
      if view_model_type == 'list':
        model_value = json.dumps(view_model_value)
      elif view_model_type == 'boolean':
        value = view_model_value
        value = False if value == '' or value == 0 else True
        model_value = str(value)
      else:
        if view_model_type is not None:
          model_value = str(view_model_value)
    except Exception as exc:
      log.error(exc, exc_info=True)
    return model_value
  @staticmethod
  def save_settings_from_view_model(settings_view_model, settings):
    to_commit = False
    with db.session.no_autoflush:
      for setting_wrap in settings:
        key = setting_wrap.setting.key
        try:
          if not hasattr(settings_view_model, key):
            continue
          setting_wrap.value = DataService.from_view_model_value_to_model_value(
            view_model_value = getattr(settings_view_model, key),
            view_model_type = setting_wrap.setting.data_type_key
          )
          db.session.add(setting_wrap)
          to_commit = True
        except Exception as exc:
          log.error(exc, exc_info=True)
          continue
    if to_commit:
      db.session.commit()
  @staticmethod
  def save_settings_defaults_from_view_model(settings_defaults_view_model, setting_defaults):
    to_commit = False
    with db.session.no_autoflush:
      for setting in setting_defaults:
        key = setting.key
        try:
          if not hasattr(settings_defaults_view_model, key):
            continue
          setting.default = DataService.from_view_model_value_to_model_value(
            view_model_value = getattr(settings_defaults_view_model, key),
            view_model_type = setting.data_type_key
          )
          db.session.add(setting)
          to_commit = True
        except Exception as exc:
          log.error(exc, exc_info=True)
          continue
    if to_commit:
      db.session.commit()
  # Save settings from view model
  @staticmethod
  def save_session_settings_from_view_model(session, session_settings_view_model):
    DataService.save_settings_from_view_model(settings_view_model=session_settings_view_model, settings=session.settings)
    db.session.add(session)
    db.session.commit()
  @staticmethod
  def save_profile_settings_from_view_model(profile, profile_settings_view_model):
    DataService.save_settings_from_view_model(settings_view_model=profile_settings_view_model, settings=profile.settings)
  @staticmethod
  def save_app_settings_from_view_model(app_settings_view_model):
    app_settings = AppSettings.query.all()
    app_settings_view_model.serial_key_hash = EncryptionUnit.get_hash(app_settings_view_model.serial_key_hash)
    DataService.save_settings_from_view_model(settings_view_model=app_settings_view_model, settings=app_settings)
  # Save settings defaults from view model
  @staticmethod
  def save_session_settings_defaults_from_view_model(session_settings_defaults_view_model):
    session_settings_defaults = SessionSetting.query.all()
    DataService.save_settings_defaults_from_view_model(settings_defaults_view_model=session_settings_defaults_view_model, setting_defaults=session_settings_defaults)
  @staticmethod
  def save_profile_settings_defaults_from_view_model(profile_settings_defaults_view_model):
    profile_settings_defaults = ProfileSetting.query.all()
    DataService.save_settings_defaults_from_view_model(settings_defaults_view_model=profile_settings_defaults_view_model, setting_defaults=profile_settings_defaults)
  @staticmethod
  def save_app_settings_defaults_from_view_model(app_settings_defaults_view_model):
    app_settings_defaults = AppSetting.query.all()
    DataService.save_settings_defaults_from_view_model(settings_defaults_view_model=app_settings_defaults_view_model, setting_defaults=app_settings_defaults)

