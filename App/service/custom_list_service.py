import json
from . import BaseService
from ..database import db, CustomList
from ..logger import Logger
from ..session import SessionRepository
from ..follower_following_tool import FollowerFollowingToolRepository

log = Logger.get(__name__)

list_types_keys = [
  'usernames',
  'hashtags',
  'comments',
  'locations',
  'links'
]

class CustomListService(BaseService):
  @classmethod
  def save_custom_list_from_view_model(cls, custom_list, custom_list_view_model):
    # custom_list_view_model: CustomListViewModel
    try:
      custom_list.name = custom_list_view_model.name
      custom_list.list_type_key = custom_list_view_model.list_type_key
      # Clean usernames and hashtags
      if custom_list_view_model.list_type_key == 'usernames':
        SessionRepository.clean_usernames(custom_list_view_model.value)
      elif custom_list_view_model.list_type_key == 'hashtags':
        SessionRepository.clean_hashtags(custom_list_view_model.value)
      # Clean from empty strings - needs to happen last
      custom_list_view_model.value = [s for s in custom_list_view_model.value if s != '']
      # Store as json
      custom_list.value = json.dumps(custom_list_view_model.value)
      db.session.add(custom_list)
      db.session.commit()
    except Exception as exc:
      log.error(exc, exc_info=True)
      custom_list = None
    return custom_list
  @classmethod
  def create_custom_list_from_view_model(cls, custom_list_view_model):
    # custom_list_view_model: CustomListViewModel
    custom_list = CustomList()
    return cls.save_custom_list_from_view_model(custom_list=custom_list, custom_list_view_model=custom_list_view_model)
  @classmethod
  def get_custom_lists_for_display(cls):
    custom_lists = CustomList.query.filter_by(active=True, is_system=False).all()
    tools_lists = FollowerFollowingToolRepository.get_requests()
    # Prepare return object
    custom_lists_to_return = {}
    for list_type in list_types_keys:
      custom_lists_to_return[list_type] = []
    # Fill custom lists
    for custom_list in custom_lists:
      custom_lists_to_return[custom_list.list_type_key].append({
        'id' : custom_list.id,
        'name': custom_list.name,
        'sub_type': custom_list.list_type_key,
      })
    # Tools lists needs to go under usernames
    for tools_list in tools_lists:
      custom_lists_to_return['usernames'].append({
        'id' : tools_list.id,
        'name': tools_list.session.name,
        'sub_type': 'tool_request',
      })
    return custom_lists_to_return


