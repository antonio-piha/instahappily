from .base_service import BaseService
from .data_service import DataService
from .profile_service import ProfileService
from .session_service import SessionService
from .follower_following_tool_service import FollowerFollowingToolService
from .custom_list_service import CustomListService
from .updater_service import UpdaterService

def init_app(app):
  SessionService.init_app(app)
  UpdaterService.init_app(app)
