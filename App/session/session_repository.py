import json
from ..database import db, Session, SessionSetting, SessionSettings, AppSettings, ProfileSettings, CustomList, FollowerFollowingToolRequestResult, Profile
from ..logger import SessionLoggerFilter, Logger

log = Logger.get(__name__)

class SessionRepository:
  @staticmethod
  def should_session_run_forever(session_id):
    run_forever_settings = SessionSettings.query.join(SessionSetting).filter(
      SessionSettings.session_id==session_id,
      SessionSetting.key=='run_forever',
      SessionSettings.value=='True').first()
    return True if run_forever_settings is not None else False
  @staticmethod
  def optional(value):
    if value == '':
      return None
    return value
  @staticmethod
  def get_percentage(number):
    # get_percentage is actually dealing with mathematical combinations
    # the number it recieves will represents "every N-th" from the set
    # The result is visualised as percentage
    max = 100
    min = 0
    if number is None:
      return max
    if number <= 0:
      return min
    tmp_number = number
    while tmp_number > 100:
      max = max * 10
      tmp_number = tmp_number / 100
    rounded = round((max/int(number)))
    return rounded if rounded >=1 else min
  @classmethod
  def get_sessions_to_run_on_app_startup(cls, active=True, is_system=False):
    # Combination of persistent sessions and sessions in progress
    return Session.query.join(SessionSettings).join(SessionSetting).filter(
      (
        (SessionSetting.key == 'run_forever') & (SessionSettings.value == 'True')
      ) | ( # or
        (Session.start_datetime != None) & (Session.start_datetime >= Session.end_datetime)
      ) | ( # or
        (Session.start_datetime != None) & (Session.end_datetime == None)
      )
    ).filter( # and
      Session.active == active,
      Session.is_system == is_system
    ).all()
  @classmethod
  def get_persistent_sessions(cls, active=True, is_system=False):
    return Session.query.join(SessionSettings).join(SessionSetting).filter(
      SessionSetting.key == 'run_forever',
      SessionSettings.value == 'True',
      Session.active == active,
      Session.is_system == is_system
    ).all()
  @classmethod
  def get_in_progress_sessions(cls, active=True, is_system=False):
    return Session.query.filter(
      Session.start_datetime != None,
      Session.start_datetime >= Session.end_datetime,
      Session.active == active,
      Session.is_system == is_system
    ).all()
  @staticmethod
  def create_session(name, profile_id, skip_settings=None, is_system=False):
    session = None
    try:
      session = Session().create(name, profile_id, is_system=is_system)
      if not skip_settings:
        settings = SessionSetting.query.all()
        for setting in settings:
          db.session.add(SessionSettings(session_id=session.id, setting_id=setting.id, value=setting.default))
        db.session.commit()
    except Exception as exc:
      session = None
      log.error(exc, exc_info=True)
    return session
  @staticmethod
  def duplicate_session(session_id):
    session = None
    try:
      session_to_duplicate = Session.query.filter_by(id=session_id).first()
      settings_to_duplicate = session_to_duplicate.settings
      new_name = "Copy of - {}".format(session_to_duplicate.name)
      session = Session().create(new_name, session_to_duplicate.profile_id)
      settings = SessionSetting.query.all()
      for setting in settings:
        value = ''
        for setting_to_duplicate in settings_to_duplicate:
          if setting.key == setting_to_duplicate.setting.key:
            value = setting_to_duplicate.value
            break
        db.session.add(SessionSettings(session_id=session.id, setting_id=setting.id, value=value))
      db.session.commit()
    except Exception as exc:
      session = None
      log.error(exc, exc_info=True)
    return session
  @classmethod
  def is_value_empty(cls, value):
    return value is None or (not value and value != 0)
  @classmethod
  def provision_settings(cls, session_meta):
    # Provision settings to make possible settings hierarchy app / profile / session
    settings = session_meta.settings
    for key, value in session_meta.session_settings.__dict__.items():
      if hasattr(settings, key):
        setattr(settings, key, value)
    # settings is a combined object of several clases, and multi inheritance
    # won't return all the atributes if used like settings.__dict__.items()
    keys = list(k for k in dir(settings) if not k.startswith('__'))
    for key in keys:
      value = getattr(settings, key)
      checking_value = value
      if cls.is_value_empty(checking_value):
        if hasattr(session_meta.profile_settings, key):
          checking_value = getattr(session_meta.profile_settings, key)
          if not cls.is_value_empty(checking_value):
            setattr(settings, key, checking_value)
            continue
        if hasattr(session_meta.app_settings, key):
          checking_value = getattr(session_meta.app_settings, key)
          if not cls.is_value_empty(checking_value):
            setattr(settings, key, checking_value)
            continue
    session_meta.settings = settings
  @classmethod
  def resolve_custom_lists(cls, session_settings_view_model, session_settings_model):
    if session_settings_view_model is None or session_settings_model is None:
      log.error('session_settings_view_model or session_settings_model is None')
      return
    for session_setting_model in session_settings_model:
      # Objects only, skip the rest data types
      if session_setting_model.setting.data_type_key != 'object':
        continue
      # model_value: { id: "", name: "", "list_type": ""}
      # List type holds the info is this list :
      # - Custom list
      # - Tool request
      model_value = session_setting_model.value
      value = None
      if model_value is not None and model_value != '':
        # Load JSON
        try:
          model_value = json.loads(model_value)
        except Exception as exc:
          model_value = None
        if type(model_value) is dict:
          list_id = model_value.get('id') # String
          if list_id.isdigit():
            list_id = int(list_id)
          list_type = model_value.get('list_type')
          # Tool request
          if list_type == 'tool_request':
            tool_request_result = FollowerFollowingToolRequestResult.query.filter_by(id=list_id).first()
            tool_result = None
            result_type_key = None
            if tool_request_result:
              tool_result_type_setting = SessionSettings.query.join(Session).join(SessionSetting).filter(
                Session.id == tool_request_result.session_id,
                SessionSetting.key == 'follower_following_tool_type'
              ).first()
              if tool_result_type_setting:
                result_type_key = tool_result_type_setting.value
              try:
                tool_result = json.loads(tool_request_result.result)
              except Exception as exc:
                tool_result = None
            if tool_result and result_type_key:
              value = tool_result[result_type_key]
          # Custom list
          else:
            custom_list = None
            custom_list_model = CustomList.query.filter_by(id=list_id).first()
            if custom_list_model:
              custom_list = custom_list_model.value
            if custom_list:
              # Load JSON
              try:
                value = json.loads(custom_list)
              except Exception as exc:
                value = []
      else:
        value = []
      key = session_setting_model.setting.key
      setattr(session_settings_view_model, key, value)
  @classmethod
  def populate_session_meta(cls, session_meta):
    #
    # This is here because it is cause/victim of circular imports
    #
    from ..view_model import SessionSettingsViewModel, ProfileSettingsViewModel, AppSettingsViewModel, SessionMetaSettingsViewModel

    try:
      # Get session
      session = Session.query.filter_by(id=session_meta.session_id).first()
      if not session:
        # Session is important
        return None
      session_meta.session = session
      session_meta.settings = SessionMetaSettingsViewModel()
      session_meta.logger_filter = SessionLoggerFilter()
      # App settings
      app_settings = AppSettings.query.all()
      session_meta.app_settings = AppSettingsViewModel().set_from_model(model=app_settings)
      # Profile settings
      profile = session.profile
      session_meta.username = profile.username
      session_meta.passwords['profile'] = profile.get_password()
      profile_settings = ProfileSettings.query.filter_by(profile_id=profile.id).all()
      session_meta.profile_settings = ProfileSettingsViewModel().set_from_model(profile_settings)
      # Session settings
      session_settings = SessionSettings.query.filter_by(session_id=session.id)
      session_meta.session_settings = SessionSettingsViewModel().set_from_model(session_settings)
      # Proxy settings
      proxy = profile.proxy
      if proxy:
        session_meta.proxy = proxy
        session_meta.passwords['proxy'] = proxy.get_password()
      # Resolve custom lists
      cls.resolve_custom_lists(
        session_settings_view_model=session_meta.session_settings,
        session_settings_model=session_meta.session.settings
      )
      # Must be last - populates session_meta.settings object which is used in submodules
      cls.provision_settings(session_meta)
    except Exception as exc:
        log.error(exc, exc_info=True)
    return session_meta
  @classmethod
  def save_session_settings(cls, session, session_settings_view_model):
    #
    # This is here because it is cause/victim of circular imports
    #
    from ..service import DataService

    # clean hashtags
    cls.clean_hashtags(session_settings_view_model.like_by_tags_list)
    cls.clean_hashtags(session_settings_view_model.follow_by_tags_list)
    cls.clean_hashtags(session_settings_view_model.skip_and_avoid_hashtags_list)
    cls.clean_hashtags(session_settings_view_model.smart_hashtags_list)
    # clean usernames
    cls.clean_usernames(session_settings_view_model.like_by_user_list)
    cls.clean_usernames(session_settings_view_model.ignore_users_by_user_list)
    cls.clean_usernames(session_settings_view_model.follow_username_list)
    cls.clean_usernames(session_settings_view_model.follow_user_followers_list)
    cls.clean_usernames(session_settings_view_model.follow_user_following_list)
    cls.clean_usernames(session_settings_view_model.follow_likers_list)
    cls.clean_usernames(session_settings_view_model.follow_commenters_list)
    cls.clean_usernames(session_settings_view_model.unfollow_custom_list)
    cls.clean_usernames(session_settings_view_model.interact_by_users_list)
    cls.clean_usernames(session_settings_view_model.interact_by_users_tagged_posts_list)
    cls.clean_usernames(session_settings_view_model.interact_by_users_following_list)
    cls.clean_usernames(session_settings_view_model.interact_by_user_followers_list)
    cls.clean_usernames(session_settings_view_model.interact_by_comments_users_list)
    cls.clean_usernames(session_settings_view_model.exclude_friends_list)
    cls.clean_usernames(session_settings_view_model.follower_following_tool_target_user_list)
    # Clean lists from empty strings - needs to happen after other cleanups
    try:
      for key, item in session_settings_view_model.__dict__.items():
        if isinstance(item, list):
          _cleared_list = [s for s in item if s != '']
          item.clear()
          item.extend(_cleared_list)
    except Exception as exc:
      log.error(exc, exc_info=True)
    session.name = session_settings_view_model.session_name
    # To force loading from DB
    session_settings = session.settings
    DataService.save_session_settings_from_view_model(
      session = session,
      session_settings_view_model = session_settings_view_model
    )
    return (session_settings, session_settings_view_model)
  @classmethod
  def clean_list_of_strings(cls, list_of_strings, to_clean=None):
    try:
      cleaned = []
      if list_of_strings and to_clean:
        cleaned = [s.replace(to_clean, '') for s in list_of_strings]
      list_of_strings.clear()
      list_of_strings.extend(cleaned)
    except Exception as exc:
      log.error(exc, exc_info=True)
  @classmethod
  def clean_hashtags(cls, list_of_hashtags):
    cls.clean_list_of_strings(list_of_hashtags, '#')
  @classmethod
  def clean_usernames(cls, list_of_usernames):
    cls.clean_list_of_strings(list_of_usernames, '@')
  @classmethod
  def is_session_running(cls, session):
    running = False
    if not session:
      return running
    if (session.start_datetime is None and session.end_datetime is None):
      running = False
    elif (session.start_datetime is not None and session.end_datetime is None):
      running = True
    elif session.start_datetime >= session.end_datetime:
      running = True
    else:
      running = False
    return running
  @staticmethod
  def filter_sessions_with_proxy_enabled(sessions):
    sessions_with_proxy_enabled = []
    try:
      enabled_proxies = Profile.query.filter(Profile.proxy_id != None).filter(Profile.proxy_id != '').all()
      profile_ids_with_proxies = [p.id for p in enabled_proxies]
      sessions_with_proxy_enabled = [s for s in sessions if s.profile_id in profile_ids_with_proxies]
    except Exception as exc:
      log.error(exc, exc_info=True)
      sessions_with_proxy_enabled = []
    return sessions_with_proxy_enabled
