import json
from ..service import DataService
from ..logger import Logger
from ..database import initial_values_session_setting, initial_values_profile_setting, initial_values_app_settings, password_magic_word_if_stored

log = Logger.get(__name__)

# View models Base classes
class ViewModelBase():
  def set_from_model(self, model):
    return self

class SettingsViewModelBase(ViewModelBase):
  def set_from_model(self, model):
    if model is not None:
      for item in model:
        if item.setting:
          value = DataService.from_setting_model_value_to_setting_view_model_value(item.value, item.setting.data_type_key)
          setattr(self, item.setting.key, value)
    return self

class SettingsDefaultsViewModelBase(ViewModelBase):
  def set_from_model(self, model):
    if model is not None:
      for item in model:
        default = DataService.from_setting_model_value_to_setting_view_model_value(item.default, item.data_type_key)
        setattr(self, item.key, default)
    return self


# Dinamically building types
###############################################
def build_view_models():
  view_models = {}
  # Session
  session_settings_view_model = {}
  for setting in initial_values_session_setting:
    session_settings_view_model[setting.key] = None
  view_models['SessionSettingsViewModelBase'] = type('SessionSettingsViewModelBase', (SettingsViewModelBase,), session_settings_view_model)
  view_models['SessionSettingsDefaultsViewModelBase'] = type('SessionSettingsDefaultsViewModelBase', (SettingsDefaultsViewModelBase,), session_settings_view_model)
  # Profile
  profile_settings_view_model = {}
  for setting in initial_values_profile_setting:
    profile_settings_view_model[setting.key] = None
  view_models['ProfileSettingsViewModelBase'] = type('ProfileSettingsViewModelBase', (SettingsViewModelBase,), profile_settings_view_model)
  view_models['ProfileSettingsDefaultsViewModelBase'] = type('ProfileSettingsDefaultsViewModelBase', (SettingsDefaultsViewModelBase,), profile_settings_view_model)
  # App
  app_settings_view_model = {}
  for setting in initial_values_app_settings:
    app_settings_view_model[setting.key] = None
  view_models['AppSettingsViewModelBase'] = type('AppSettingsViewModelBase', (SettingsViewModelBase,), app_settings_view_model)
  view_models['AppSettingsDefaultsViewModelBase'] = type('AppSettingsDefaultsViewModelBase', (SettingsDefaultsViewModelBase,), app_settings_view_model)
  return view_models

try:
  view_model_base_classes = build_view_models()
  SessionSettingsViewModelBase = view_model_base_classes['SessionSettingsViewModelBase']
  SessionSettingsDefaultsViewModelBase = view_model_base_classes['SessionSettingsDefaultsViewModelBase']
  ProfileSettingsViewModelBase = view_model_base_classes['ProfileSettingsViewModelBase']
  ProfileSettingsDefaultsViewModelBase = view_model_base_classes['ProfileSettingsDefaultsViewModelBase']
  AppSettingsViewModelBase = view_model_base_classes['AppSettingsViewModelBase']
  AppSettingsDefaultsViewModelBase = view_model_base_classes['AppSettingsDefaultsViewModelBase']
except Exception as exc:
  log.error(exc, exc_info=True)
###############################################

class SessionSettingsViewModel(SessionSettingsViewModelBase):
  session_name = None
  pass
class SessionSettingsDefaultsViewModel(SessionSettingsDefaultsViewModelBase):
  pass
class ProfileSettingsViewModel(ProfileSettingsViewModelBase):
  pass
class ProfileSettingsDefaultsViewModel(ProfileSettingsDefaultsViewModelBase):
  pass
class AppSettingsViewModel(AppSettingsViewModelBase):
  def set_from_model(self, model):
    super(AppSettingsViewModelBase, self).set_from_model(model)
    if hasattr(self, 'serial_key_hash') and getattr(self, 'serial_key_hash') != '':
      setattr(self, 'serial_key_hash', '*******************************************************')
      return self
class AppSettingsDefaultsViewModel(AppSettingsDefaultsViewModelBase):
  pass

class SessionMetaSettingsViewModel(SessionSettingsViewModel, ProfileSettingsViewModel, AppSettingsViewModel):
  pass

class ProxyViewModel(ViewModelBase):
  name = None
  ip = None
  port = None
  username = None
  password = None
  active = None
  def set_from_model(self, model):
    if model is not None:
      self.name = model.name
      self.ip = model.ip
      self.port = model.port
      self.username = model.username
      password = model.get_password()
      if password != '':
        self.password = password_magic_word_if_stored
      # Active field is stored as boolean in DB (not as string)
      self.active = model.active
    return self

class FollowerFollowingToolViewModel(SessionSettingsViewModel):
  follower_following_tool_profile_id=None
  def set_from_model(self, model):
    # model: FollowerFollowingToolRequestResult
    super(SessionSettingsViewModelBase, self).set_from_model(model.session.settings)
    self.session_name = model.session.name
    if model.profile_id:
      self.follower_following_tool_profile_id = model.profile_id
    return self

class CustomListViewModel(ViewModelBase):
  name= None
  list_type_key = None
  value = None
  def set_from_model(self, model):
    if model is not None:
      self.name = model.name
      self.list_type_key = model.list_type_key
      self.value = DataService.from_model_value_to_view_model_value(model.value, 'list')
    return self
