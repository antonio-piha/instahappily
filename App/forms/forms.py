from flask_wtf import FlaskForm
from wtforms import SubmitField, FormField, IntegerField
from wtforms.validators import DataRequired, IPAddress
from .fields import build_field, IStringField, IPasswordField, SubmitField, IHiddenField, IIntegerField, IDecimalField, IFieldList, IBooleanField, FormField
from ..database import initial_values_session_setting, initial_values_profile_setting, initial_values_app_settings
from ..logger import Logger
from ..view_model import SessionSettingsViewModel, SessionSettingsDefaultsViewModel, ProfileSettingsViewModel, AppSettingsViewModel, ProxyViewModel, FollowerFollowingToolViewModel, CustomListViewModel

log = Logger.get(__name__)

# Common
class BaseForm(FlaskForm):
  def set_from_view_model(self, view_model):
    if not view_model:
      log.error("View model is None or empty.")
      return
    for name, field in self._fields.items():
      try:
        if not hasattr(view_model, name):
          continue
        if field.type == 'list':
          entries = getattr(view_model, name, [])
          field.clear()
          field.append(entries)
        else:
          field.data = getattr(view_model, name)
      except Exception as exc:
        log.error(exc, exc_info=True)
    return self
  def to_view_model(self, view_model):
    for name, field in self._fields.items():
      try:
        if not hasattr(view_model, name) or field is None:
          continue
        value = field.data
        if field.type == 'boolean':
          value = False if value == '' or value == 0 else True
        setattr(view_model, name, value)
      except Exception as exc:
        log.error(exc, exc_info=True)
    return view_model

class BaseConfirmForm(FlaskForm):
  confirm = IHiddenField('Confirm', [])



# Dinamically building types
###############################################
def build_settings_forms():
  forms = {}
  # Session settings form
  session_settings_forms = {}
  for setting in initial_values_session_setting:
    session_settings_forms[setting.key] = build_field(setting)
  forms['SessionSettingsBaseForm'] = type('SessionSettingsBaseForm', (BaseForm,), session_settings_forms)
  # Profile settings form
  profile_settings_forms = {}
  for setting in initial_values_profile_setting:
    profile_settings_forms[setting.key] = build_field(setting)
  forms['ProfileSettingsBaseForm'] = type('ProfileSettingsBaseForm', (BaseForm,), profile_settings_forms)
  # App settings form
  app_settings_forms = {}
  for setting in initial_values_app_settings:
    app_settings_forms[setting.key] = build_field(setting)
  forms['AppSettingsBaseForm'] = type('AppSettingsBaseForm', (BaseForm,), app_settings_forms)
  return forms

try:
  forms_base_classes = build_settings_forms()
  SessionSettingsBaseForm = forms_base_classes['SessionSettingsBaseForm']
  ProfileSettingsBaseForm = forms_base_classes['ProfileSettingsBaseForm']
  AppSettingsBaseForm = forms_base_classes['AppSettingsBaseForm']
except Exception as exc:
  log.error(exc, exc_info=True)
###############################################

class SessionSettingsDefaultsForm(SessionSettingsBaseForm):
  def to_view_model(self):
    return super(SessionSettingsDefaultsForm, self).to_view_model(SessionSettingsDefaultsViewModel())

class SessionSettingsForm(SessionSettingsBaseForm):
  session_name = IStringField("session_name", [DataRequired()])
  def to_view_model(self):
    return super(SessionSettingsForm, self).to_view_model(SessionSettingsViewModel())

class ProfileSettingsForm(ProfileSettingsBaseForm):
  def to_view_model(self):
    return super(ProfileSettingsForm, self).to_view_model(ProfileSettingsViewModel())

class AppSettingsForm(AppSettingsBaseForm):
  def to_view_model(self):
    return super(AppSettingsForm, self).to_view_model(AppSettingsViewModel())


# Session
class SessionAddForm(FlaskForm):
  name = IStringField('Name', [DataRequired()])
  profile_id = IHiddenField('Profile', [])
  submit = SubmitField('Add')
class SessionDeactivateForm(BaseConfirmForm):
  pass
class SessionActivateForm(BaseConfirmForm):
  pass
class SessionStartForm(BaseConfirmForm):
  pass
class SessionDuplicateForm(BaseConfirmForm):
  pass
class SessionStopForm(BaseConfirmForm):
  pass
class ActionAllSessionsForProfile(BaseConfirmForm):
  pass


# Proxy
class ProxyAddForm(BaseForm):
  name = IStringField('Name', [DataRequired()])
  ip = IStringField('Ip', [DataRequired()])
  port = IStringField('Port', [DataRequired()])
  username = IStringField('Username')
  password = IPasswordField('Password')
  active = IBooleanField('Active')
  def to_view_model(self):
    return super(ProxyAddForm, self).to_view_model(ProxyViewModel())
class ProxyEditForm(ProxyAddForm):
  pass
class ProxyActivateForm(BaseConfirmForm):
  pass
class ProxyDeactivateForm(BaseConfirmForm):
  pass


# Profile
class ProfileAddForm(BaseForm):
  username = IStringField('Username', [DataRequired()])
  password = IPasswordField('Password', [DataRequired()])
  submit = SubmitField('Add')
class ProfileEditForm(ProfileSettingsForm):
  password = IPasswordField('Password', [])
  proxy_id = IIntegerField('ProxyId', [])
  submit = SubmitField('Save')
class ProfileDeactivateForm(BaseConfirmForm):
  pass
class ProfileActivateForm(BaseConfirmForm):
  pass



# Tools
class FollowerFollowingToolForm(SessionSettingsForm):
  follower_following_tool_profile_id = IIntegerField('ProfileId', [])
  submit = SubmitField('Save')
  def to_view_model(self):
    return super(SessionSettingsBaseForm, self).to_view_model(FollowerFollowingToolViewModel())
class ActionAllFollowerFollowingToolForm(BaseConfirmForm):
  pass


# CustomList
class CustomListAddForm(BaseForm):
  name = IStringField('Name', [DataRequired()])
  list_type_key = IStringField('ListTypeKey', [DataRequired()])
  value = IFieldList(IStringField())
  def to_view_model(self):
    return super(CustomListAddForm, self).to_view_model(CustomListViewModel())