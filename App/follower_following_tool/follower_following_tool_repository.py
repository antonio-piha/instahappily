import json
from ..logger import Logger
from ..database import db, FollowerFollowingToolRequestResult, Session

log = Logger.get(__name__)

class FollowerFollowingToolStatuses:
  done = '_DONE_'
  running = '_RUNNING_'
  failed = '_FAILED_'
  pending = '_PENDING_'


follower_following_tool_key_name = {
  'followers': 'Followers',
  'followings': 'Followings',
  'nonfollowers': 'Non-followers',
  'all_unfollowers': 'All unfollowers',
  'active_unfollowers': 'Active unfollowers',
  'fans': 'Fans',
  'mutual_following': 'Mutual following'
}

class SetEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, set):
      return list(obj)
    return json.JSONEncoder.default(self, obj)

class FollowerFollowingToolResult():
  def __init__(self):
    self.followers = set()
    self.followings = set()
    self.nonfollowers = set()
    self.fans = set()
    self.mutual_following = set()
    self.all_unfollowers = set()
    self.active_unfollowers = set()

class FollowerFollowingToolRequestDisplayInfo():
  def __init__(self):
    self.request_id=None
    self.request_name=None
    self.profile_name=None
    self.target_users=None
    self.tool_type_key=None
    self.tool_type_name=None
    self.result=None
    self.status=None

class FollowerFollowingToolRepository():
  @staticmethod
  def create(session_id, profile_id, is_system=False):
    model = None
    try:
      model = FollowerFollowingToolRequestResult(session_id=session_id, profile_id=profile_id, is_system=is_system)
      db.session.add(model)
      db.session.commit()
    except Exception as exc:
      log.error(exc, exc_info=True)
      model = None
    return model
  @staticmethod
  def save_request(model):
    try:
      db.session.add(model)
      db.session.commit()
    except Exception as exc:
      log.error(exc, exc_info=True)
      return None
    return model
  @classmethod
  def save_result(cls, model, result):
    saved = False
    try:
      if model:
        if isinstance(result, FollowerFollowingToolResult):
          model.result = json.dumps(result.__dict__, cls=SetEncoder)
        else:
          model.result = result
        db.session.add(model)
        db.session.commit()
        saved = True
    except Exception as exc:
      log.error(exc, exc_info=True)
      saved = False
    return saved
  @classmethod
  def save_result_by_session(cls, session_id, result):
    saved = False
    try:
      model = FollowerFollowingToolRequestResult.query.filter_by(session_id=session_id).first()
      saved = cls.save_result(model, result)
    except Exception as exc:
      log.error(exc, exc_info=True)
      saved = False
    return saved
  @classmethod
  def get_requests(cls, is_system=False,active=True):
    # Map data from model to display info
    requests = []
    try:
      requests = FollowerFollowingToolRequestResult.query.join(Session).filter(
        FollowerFollowingToolRequestResult.active == active,
        FollowerFollowingToolRequestResult.is_system == is_system
      ).order_by(FollowerFollowingToolRequestResult.id.desc()).all()
    except Exception as exc:
      log.error(exc, exc_info=True)
      requests = None
    return requests

