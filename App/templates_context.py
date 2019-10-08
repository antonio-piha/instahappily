from wtforms.fields import Flags
from .service import SessionService
from .database import AppSettings, AppSettings, Profile, Proxy
from .view_model import AppSettingsViewModel
from .settings import Settings

_context = {}

def generate():
  get_app_settings()
  return _context

def init_app(app):
  # Templates global
  # Executed for each request, not on app start
  app.context_processor(inject_context_for_all_templates)

def inject_context_for_all_templates():
  dict_context = generate()
  return dict_context
###################################################

_context['app_version'] = Settings.app_version

_context['SessionService'] = SessionService

def list_to_dict(list_arg):
  return {k:v for k,v in zip(list_arg,list_arg)}
_context['list_to_dict'] = list_to_dict

def get_object_keys(object_to_process):
  return list(k for k in dir(object_to_process) if not k.startswith('__'))
_context['get_object_keys'] = get_object_keys

def get_possible_values_from_object_list(list_of_objects, value_key='id', name_key='name'):
  value_list = []
  name_list = []
  for obj in list_of_objects:
    value_list.append(getattr(obj, value_key, ''))
    name_list.append(getattr(obj, name_key, ''))
  return {k:v for k,v in zip(value_list, name_list)}
_context['get_possible_values_from_object_list'] = get_possible_values_from_object_list

def get_app_settings():
  app_settings = AppSettings.query.all()
  _context['app_settings'] = AppSettingsViewModel().set_from_model(app_settings)

def make_field_required(field):
  setattr(field.flags, 'required', True)
  return field
_context['make_field_required'] = make_field_required

def get_visibility_classes(visible=None):
  visibility_classes = ''
  if visible:
    # js-advanced advanced, second is css
    visibility_classes = 'js-visibility-toggle js-{} {}'.format(visible, visible)
    if (visible == 'advanced' and _context['app_settings'].settings_view_level == 'simple'
      ) or (
      visible == 'expert' and _context['app_settings'].settings_view_level != 'expert'):
      visibility_classes = '{} d-none'.format(visibility_classes)
  return visibility_classes
_context['get_visibility_classes'] = get_visibility_classes

def get_all_profiles_as_possible_values():
  profiles = Profile.query.filter_by(active=True).all()
  return {profile.id:profile.username for profile in profiles}
_context['get_all_profiles_as_possible_values'] = get_all_profiles_as_possible_values

def get_all_proxies_as_possible_values():
  proxies = Proxy.query.filter_by(active=True).all()
  return get_possible_values_from_object_list(proxies)
_context['get_all_proxies_as_possible_values'] = get_all_proxies_as_possible_values