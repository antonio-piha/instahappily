import random
import json
from . import BaseService
from . import SessionService
from ..database import FollowerFollowingToolRequestResult, Profile
from ..logger import Logger
from ..session import SessionRepository
from ..session.session_submodule import session_follower_following_tool
from ..follower_following_tool import FollowerFollowingToolRepository, FollowerFollowingToolStatuses, FollowerFollowingToolRequestDisplayInfo, follower_following_tool_key_name

log = Logger.get(__name__)


class FollowerFollowingToolService(BaseService):
  @classmethod
  def _start_session(cls, session_id):
    run = SessionService.start_session(session_id=session_id,
      workload_function=session_follower_following_tool)
    return run
  @classmethod
  def start_request(cls, request_id):
    run = False
    try:
      tool_request_result = FollowerFollowingToolRequestResult.query.filter_by(id=request_id).first()
      if tool_request_result:
        # Set result to empty/None because of request status
        run = cls._start_session(tool_request_result.session.id)
    except Exception as exc:
      log.error(exc, exc_info=True)
      run = False
    return run
  @classmethod
  def stop_request(cls, request_id):
    stopped = False
    try:
      tool_request_result = FollowerFollowingToolRequestResult.query.filter_by(id=request_id).first()
      if tool_request_result:
        stopped = SessionService.stop_session(tool_request_result.session.id)
        # Set result to failed if we stop the session while it was still running
        if SessionRepository.is_session_running(tool_request_result.session):
          FollowerFollowingToolRepository.save_result(tool_request_result, FollowerFollowingToolStatuses.failed)
    except Exception as exc:
      log.error(exc, exc_info=True)
      stopped = True
    return run
  @classmethod
  def save_request_from_view_model(cls, request, request_view_model):
    # request_view_model: FollowerFollowingToolViewModel
    request = None
    try:
      session = request.session
      if session:
        SessionRepository.save_session_settings(
          session = session,
          session_settings_view_model = request_view_model
        )
      # Change profile id only if it's really changed
      if (request_view_model.profile_id != '' and request_view_model.profile_id != None
        and request.profile_id != request_view_model.profile_id):
        request.profile_id = request_view_model.profile_id
      request = FollowerFollowingToolRepository.save_request(request)
    except Exception as exc:
      log.error(exc, exc_info=True)
      request = None
    return request
  @classmethod
  def create_request_from_view_model(cls, request_view_model):
    # request_view_model: FollowerFollowingToolViewModel
    request = None
    try:
      # If profile_id is not set get the random one from DB
      profile_id = request_view_model.follower_following_tool_profile_id
      if not profile_id or profile_id == '' or profile_id == None:
        profile_count = Profile.query.filter_by(active=True).count()
        profile_id = random.randint(1,profile_count)
      else:
        # Expecting integer
        profile_id = int(profile_id)
      session = SessionRepository.create_session(
        name=request_view_model.session_name,
        profile_id=profile_id,
        is_system=True
        )
      if session:
        SessionRepository.save_session_settings(
          session = session,
          session_settings_view_model = request_view_model
        )
        request = FollowerFollowingToolRepository.create(
              session_id=session.id,
              profile_id=profile_id)
      cls._start_session(session.id)
    except Exception as exc:
      log.error(exc, exc_info=True)
      request = None
    return request
  @classmethod
  def from_request_to_display_info(cls, request):
    ## Cause/victim of circular imports
    #
    from ..view_model import FollowerFollowingToolViewModel

    display_info = None
    try:
      session = request.session
      view_model = FollowerFollowingToolViewModel()
      view_model.set_from_model(request)
      # Display info
      display_info = FollowerFollowingToolRequestDisplayInfo()
      display_info.profile_name = request.profile.username
      display_info.request_id = request.id
      display_info.request_name = session.name
      # Status
      # This is SessionRepository that is checked here
      if session.start_datetime is None and request.result == None:
        display_info.status = FollowerFollowingToolStatuses.pending
      elif SessionRepository.is_session_running(session):
        display_info.status = FollowerFollowingToolStatuses.running
      elif request.result != FollowerFollowingToolStatuses.failed:
        display_info.status = FollowerFollowingToolStatuses.done
      else:
        display_info.status = FollowerFollowingToolStatuses.failed
      display_info.tool_type_key = view_model.follower_following_tool_type
      display_info.tool_type_name = follower_following_tool_key_name.get(view_model.follower_following_tool_type, '')
      # Target users
      display_info.target_users = ""
      if view_model.follower_following_tool_target_user_list:
        list_of_users = view_model.follower_following_tool_target_user_list
        display_info.target_users = ", ".join(list_of_users)

      # Skipped so far
      #view_model.follower_following_tool_grab_amount
      #view_model.follower_following_tool_unfollowers_compare_by
      #view_model.follower_following_tool_unfollowers_compare_track
      # Result
      if display_info.status == FollowerFollowingToolStatuses.done:
        result = ""
        try:
          result = json.loads(request.result)
          result = result.get(view_model.follower_following_tool_type, [])
        except Exception as exc:
          log.error(exc, exc_info=True)
        display_info.result = result
    except Exception as exc:
      log.error(exc, exc_info=True)
      display_info = None
    return display_info
  @classmethod
  def get_requests(cls, is_system=False,active=True):
    requests_as_display_infos = []
    try:
      requests = FollowerFollowingToolRepository.get_requests(is_system=is_system,active=active)
      if requests:
        for request in requests:
          requests_as_display_infos.append(cls.from_request_to_display_info(request))
    except Exception as exc:
      log.error(exc, exc_info=True)
      requests_as_display_infos = None
    return requests_as_display_infos