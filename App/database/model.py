
import os
import base64
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import UniqueConstraint
from ..security import EncryptionUnit
from ..logger import Logger
from .database import db, password_magic_word_if_stored

log = Logger.get(__name__)

# Models
# InstaPy DB models
class InstaPySqliteSequence(db.Model):
  __tablename__ = 'sqlite_sequence'
  __bind_key__ = 'instapy'
  seq = db.Column(db.Text, primary_key=True)
  name = db.Column(db.Text)

class InstaPyProfiles(db.Model):
  __tablename__ = 'profiles'
  __bind_key__ = 'instapy'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text, nullable=False)

class InstaPyRecordActivity(db.Model):
  __tablename__ = 'recordActivity'
  __bind_key__ = 'instapy'
  profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
  likes = db.Column(db.Integer, nullable=False)
  comments = db.Column(db.Integer, nullable=False)
  follows = db.Column(db.Integer, nullable=False)
  unfollows = db.Column(db.Integer, nullable=False)
  server_calls = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, nullable=False)

class ShareWithPodsRestrictionActivity(db.Model):
  __tablename__ = 'shareWithPodsRestriction'
  __bind_key__ = 'instapy'
  profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
  postid = db.Column(db.Text, nullable=False)
  times = db.Column(db.Integer, nullable=False)

class InstaPyFollowRestriction(db.Model):
  __tablename__ = 'followRestriction'
  __bind_key__ = 'instapy'
  profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
  username = db.Column(db.Text, nullable=False)
  times = db.Column(db.Integer, nullable=False)

class InstaPyAccountsProgress(db.Model):
  __tablename__ = 'accountsProgress'
  __bind_key__ = 'instapy'
  profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
  followers = db.Column(db.Integer, nullable=False)
  following = db.Column(db.Integer, nullable=False)
  total_posts = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, nullable=False)
  modified = db.Column(db.DateTime, nullable=False)

# App DB models
# Order as they're used
class BaseModel(db.Model):
  __abstract__ = True
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.Text, unique=True, nullable=False)
  active = db.Column(db.Boolean, default=True, nullable=False)
  def __init__(self, **kwargs):
    self.key = kwargs.pop('key',
      base64.b64encode(os.urandom(64)).decode('UTF-8')
    )
  def __repr__(self):
    return 'id: {}, key: {}, active: {}'.format(self.id, self.key, self.active)
  def _commit(self):
    db.session.add(self)
    db.session.commit()
  def activate(self, active=True):
    self.active = active
    self._commit()
  def deactivate(self):
    self.activate(False)

class BaseCredentialsModel(BaseModel):
  __abstract__ = True
  username = db.Column(db.Text(), unique=False, nullable=False)
  password = db.Column(db.LargeBinary(), unique=False, nullable=False)
  password_tag = db.Column(db.LargeBinary(), unique=False, nullable=False)
  password_nonce = db.Column(db.LargeBinary(), unique=False, nullable=False)
  def __init__(self, **kwargs):
    super(BaseCredentialsModel, self).__init__(**kwargs)
  def __repr__(self):
    return '{}, username: {}'.format(super(BaseCredentialsModel, self).__repr__(), self.username)
  def set_password(self, plain_password):
    encrypted = EncryptionUnit(plain_password).encrypt()
    self.password = encrypted.data
    self.password_tag = encrypted.tag
    self.password_nonce = encrypted.nonce
  def get_password(self):
    return EncryptionUnit(self.password, self.password_tag, self.password_nonce).decrypt().data
  def update_password(self, plain_password):
    self.set_password(plain_password)
    self._commit()
  def create(self, username, plain_password):
    self.save(username=username, plain_password=plain_password)
    return self
  def save(self, plain_password=None, username=None):
    if username is not None:
      self.username = username
    current_password = self.get_password()
    if not current_password:
      # password is mandatory
      plain_password = plain_password if plain_password else ''
      self.set_password(plain_password)
    elif plain_password and plain_password != '' and plain_password != password_magic_word_if_stored and plain_password != current_password:
      self.set_password(plain_password)
    self._commit()

class BaseSetting(BaseModel):
  __abstract__ = True
  default = db.Column(db.Text, unique=False, nullable=False)
  @declared_attr
  def group_key(cls):
    return db.Column(db.Text, db.ForeignKey('setting_group.key'), nullable=False)
  @declared_attr
  def group(cls):
    return db.relationship('SettingGroup', lazy='select')
  @declared_attr
  def data_type_key(cls):
    return db.Column(db.Text, db.ForeignKey('setting_data_type.key'), nullable=False)
  @declared_attr
  def data_type(cls):
    return db.relationship('SettingDataType', lazy='select')
  def __init__(self, **kwargs):
    super(BaseSetting, self).__init__(**kwargs)
    self.group_key = kwargs.pop('group_key', None)
    self.data_type_key = kwargs.pop('data_type_key', None)
    self.default = kwargs.pop('default', None)
  def __repr__(self):
    return '{}, data_type: {}, group: {}, default: {}>'.format(super(BaseSetting, self).__repr__(), self.data_type, self.group_key, self.default)

class BaseSettings(BaseModel):
  __abstract__ = True
  value = db.Column(db.Text, unique=False, nullable=True)
  def __init__(self, **kwargs):
    super(BaseSettings, self).__init__(**kwargs)
    self.value = kwargs.pop('value', None)
  def __repr__(self):
    return '{}, value: {}'.format(super(BaseSetting, self).__repr__(), self.value)

class SettingDataType(BaseModel):
  def __init__(self, **kwargs):
    super(SettingDataType, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(SettingDataType, self).__repr__())

class SettingGroup(BaseModel):
  def __init__(self, **kwargs):
    super(SettingGroup, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(SettingGroup, self).__repr__())

class AppSetting(BaseSetting):
  def __init__(self, **kwargs):
    super(AppSetting, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(AppSetting, self).__repr__())

class SessionSetting(BaseSetting):
  def __init__(self, **kwargs):
    super(SessionSetting, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(SessionSetting, self).__repr__())

class ProfileSetting(BaseSetting):
  def __init__(self, **kwargs):
    super(ProfileSetting, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(ProfileSetting, self).__repr__())

class ProfileSettings(BaseSettings):
  profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
  profile = db.relationship('Profile')
  setting_id = db.Column(db.Integer, db.ForeignKey('profile_setting.id'))
  setting = db.relationship('ProfileSetting', lazy='select', backref=db.backref('profile_settings'))
  __table_args__ = (UniqueConstraint('profile_id', 'setting_id', name='ui_profile_settings_profile_id_setting_id'),)
  def __init__(self, **kwargs):
    super(ProfileSettings, self).__init__(**kwargs)
    self.profile_id = kwargs.pop('profile_id', None)
    self.setting_id = kwargs.pop('setting_id', None)
  def __repr__(self):
    return '<{}= {}, profile_id: {}, setting_id: {}>'.format(self.__class__.__name__, super(ProfileSettings, self).__repr__(), self.profile_id, self.setting_id)

class Profile(BaseCredentialsModel):
  proxy_id = db.Column(db.Integer, db.ForeignKey('proxy.id'))
  proxy = db.relationship('Proxy', lazy='select')
  sessions = db.relationship('Session', lazy='subquery', backref=db.backref('profile', lazy='select'))
  settings = db.relationship('ProfileSettings', lazy='subquery')
  __table_args__ = (UniqueConstraint('username', name='ui_profile_username'),)
  def __init__(self, **kwargs):
    super(Profile, self).__init__(**kwargs)
    # Make no other actions in the init, use create
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(Profile, self).__repr__())
  def create(self, username, plain_password, proxy_id=None):
    super(Profile, self).create(username=username, plain_password=plain_password)
    self.proxy_id = proxy_id
    return self
  def save(self, plain_password=None, proxy_id=None, username=None):
    self.proxy_id = proxy_id
    super(Profile, self).save(plain_password=plain_password, username=username)

class Proxy(BaseCredentialsModel):
  name = db.Column(db.Text(), unique=False, nullable=False)
  ip = db.Column(db.Text(), unique=False, nullable=False)
  port = db.Column(db.String(25), unique=False, nullable=False)
  def __init__(self, **kwargs):
    super(Proxy, self).__init__(**kwargs)
    # Make no other actions in the init, use create
  def __repr__(self):
    return '<{}= {}, name:{}, ip: {}, port: {}>'.format(self.__class__.__name__, super(Proxy, self).__repr__(), self.name, self.ip, self.port)
  def create(self, name, ip, port, username=None, plain_password=None, active=False):
    self.save(name=name, ip=ip, port=port, username=username, plain_password=plain_password, active=active)
    return self
  def save(self, name, ip, port, username=None, plain_password=None, active=False):
    self.name = name
    self.ip = ip
    self.port = port
    self.active = active
    super(Proxy, self).save(username=username, plain_password=plain_password)

class SessionSettings(BaseSettings):
  session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
  session = db.relationship('Session', lazy='select')
  setting_id = db.Column(db.Integer, db.ForeignKey('session_setting.id'))
  setting = db.relationship('SessionSetting', lazy='select', backref=db.backref('session_settings'))
  __table_args__ = (UniqueConstraint('session_id', 'setting_id', name='ui_session_settings_session_id_setting_id'),)
  def __init__(self, **kwargs):
    super(SessionSettings, self).__init__(**kwargs)
    self.session_id = kwargs.pop('session_id', None)
    self.setting_id = kwargs.pop('setting_id', None)
  def __repr__(self):
    return '<{}= {}, session_id: {}, setting_id: {}>'.format(self.__class__.__name__, super(SessionSettings, self).__repr__(), self.session_id, self.setting_id)

class Session(BaseModel):
  name = db.Column(db.Text, unique=False, nullable=True)
  start_datetime = db.Column(db.DateTime, nullable=True)
  end_datetime = db.Column(db.DateTime, nullable=True)
  profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
  is_system = db.Column(db.Boolean, default=False)
  settings = db.relationship('SessionSettings', lazy='select')
  def __init__(self, **kwargs):
    super(Session, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}, name: {}, start_datetime: {}, end_datetime: {}, profile_id: {}, is_system: {}>'.format(
      self.__class__.__name__,
      super(Session, self).__repr__(),
      self.name, self.start_datetime, self.end_datetime, self.profile_id, self.is_system)
  def create(self, name, profile_id, is_system=False):
    self.name = name
    self.profile_id = profile_id
    self.is_system = is_system
    self._commit()
    return self

class AppSettings(BaseSettings):
  setting_key = db.Column(db.Text, db.ForeignKey('app_setting.key'), nullable=False)
  setting = db.relationship('AppSetting', lazy='select', backref=db.backref('app_settings', lazy='select'))
  def __repr__(self):
    return '<{}= {}, setting_key: {}>'.format(
      self.__class__.__name__, super(AppSettings, self).__repr__(), self.setting_key)
  def __init__(self, **kwargs):
    super(AppSettings, self).__init__(**kwargs)
    self.setting_key = kwargs.pop('setting_key', None)

class FollowerFollowingToolRequestResult(BaseModel):
  session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
  session = db.relationship('Session', lazy='select')
  profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
  profile = db.relationship('Profile')
  result = db.Column(db.Text, unique=False, nullable=True)
  is_system = db.Column(db.Boolean, default=False)
  def __init__(self, **kwargs):
    super(FollowerFollowingToolRequestResult, self).__init__(**kwargs)
    self.profile_id = kwargs.pop('profile_id', None)
    self.session_id = kwargs.pop('session_id', None)
    self.result = kwargs.pop('result', None)
    self.is_system = kwargs.pop('is_system', False)
  def __repr__(self):
    return '<{}= {}, session_id={}, profile_id={}, result={}>'.format(self.__class__.__name__, super(FollowerFollowingToolRequestResult, self).__repr__(),
      self.session_id,
      self.profile_id,
      self.result
      )

class CustomListType(BaseModel):
  def __init__(self, **kwargs):
    super(CustomListType, self).__init__(**kwargs)
  def __repr__(self):
    return '<{}= {}>'.format(self.__class__.__name__, super(CustomListType, self).__repr__())

class CustomList(BaseModel):
  name = db.Column(db.Text, unique=False, nullable=True)
  list_type_key = db.Column(db.Text, db.ForeignKey('custom_list_type.key'), nullable=False)
  list_type = db.relationship('CustomListType', lazy='select', backref=db.backref('custom_lists', lazy='select'))
  value = db.Column(db.Text, unique=False, nullable=True)
  is_system = db.Column(db.Boolean, default=False)
  def __init__(self, **kwargs):
    super(CustomList, self).__init__(**kwargs)
    self.name = kwargs.pop('name', None)
    self.list_type_key = kwargs.pop('list_type_key', None)
    self.value = kwargs.pop('value', None)
    self.is_system = kwargs.pop('is_system', False)
  def __repr__(self):
    return '<{}= {}, name={}, list_type_key={}, value={}>'.format(self.__class__.__name__, super(CustomList, self).__repr__(),
      self.name,
      self.list_type_key,
      self.value
    )

