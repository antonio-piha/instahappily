import os
from InstaPy.instapy import InstaPy
from . import BaseService
from ..logger import Logger
from ..settings import Settings, InstaPySettings
from ..database import db, Profile, InstaPyRecordActivity, InstaPyProfiles, ProfileSetting, ProfileSettings
from ..utils.process_utils import Executor

log = Logger.get(__name__)

executor = Executor()

class ActivityRecord():
  def __init__(self):
    self.likes = 0
    self.comments = 0
    self.follows = 0
    self.unfollows = 0
    self.num_followers = 0
    self.num_following = 0

class ProfileService(BaseService):
  @classmethod
  def get_profile_activity_records(cls, profile):
    records = {
      'likes': [],
      'comments': [],
      'follows': [],
      'unfollows': [],
      'num_followers': [],
      'num_following': []
    }
    if not profile:
      return records
    instapy_profile = InstaPyProfiles.query.filter_by(name=profile.username).first()
    if not instapy_profile:
      return records
    profile_records = {}
    # Numbers has to be pulled from InstaPy db
    if instapy_profile:
      activity_records = InstaPyRecordActivity.query.filter_by(profile_id=instapy_profile.id).all()
      # Created field is type datetime
      # Summarise each activity by day
      for activity_record in activity_records:
        day_created = str(activity_record.created.date())
        if not day_created in profile_records:
          profile_records[day_created] = ActivityRecord()
        profile_records[day_created].likes = max(profile_records[day_created].likes, activity_record.likes)
        profile_records[day_created].comments = max(profile_records[day_created].comments, activity_record.comments)
        profile_records[day_created].follows = max(profile_records[day_created].follows, activity_record.follows)
        profile_records[day_created].unfollows = max(profile_records[day_created].unfollows, activity_record.unfollows)
    num_followers = cls.get_number_of_followers(profile)
    for num_followers_entry in num_followers:
      day_created = str(num_followers_entry['created'])
      if not day_created in profile_records:
        profile_records[day_created] = ActivityRecord()
      profile_records[day_created].num_followers = max(profile_records[day_created].num_followers, int(num_followers_entry['number']))
    num_following = cls.get_number_of_following(profile)
    for num_following_entry in num_following:
      day_created = str(num_following_entry['created'])
      if not day_created in profile_records:
        profile_records[day_created] = ActivityRecord()
      profile_records[day_created].num_following = max(profile_records[day_created].num_following, int(num_following_entry['number']))
    for created, activity_record in profile_records.items():
      records['likes'].append({
        'x': created,
        'y': activity_record.likes
      })
      records['comments'].append({
        'x': created,
        'y': activity_record.comments
      })
      records['follows'].append({
        'x': created,
        'y': activity_record.follows
      })
      records['unfollows'].append({
        'x': created,
        'y': activity_record.unfollows
      })
      records['num_followers'].append({
        'x': created,
        'y': activity_record.num_followers
      })
      records['num_following'].append({
        'x': created,
        'y': activity_record.num_following
      })
    return records
  @classmethod
  def get_data_from_special_instapy_files(cls, file_name):
    data_to_return = []
    file_location = os.path.join(InstaPySettings.log_location, file_name)
    if not os.path.exists(file_location):
      return data_to_return
    try:
      with open(file_location, 'r') as file_object:
        for line in file_object:
          data = line.split()
          if len(data) < 3:
            # Faulty line
            continue
          data_to_return.append({
            'created': '{}'.format(data[0]),
            'number': data[2]
          })
    except Exception as exc:
      # This file might not exist yet
      # It won't exist until first session runs
      log.info(exc, exc_info=True)
    return data_to_return
  @classmethod
  def get_number_of_followers(cls, profile):
    data = cls.get_data_from_special_instapy_files(os.path.join(profile.username, InstaPySettings.follower_num_txt_file))
    return data
  @classmethod
  def get_number_of_following(cls, profile):
    data = cls.get_data_from_special_instapy_files(os.path.join(profile.username, InstaPySettings.following_num_txt_file))
    return data
  @staticmethod
  def create_profile(username, plain_password):
    # Properly set InstaPy DB for this profile
    profile = None
    try:
        profile = Profile().create(username=username, plain_password=plain_password)
    except Exception as exc:
        log.error(exc, exc_info=True)
        profile = None
    if profile:
      try:
        settings = ProfileSetting.query.all()
        for setting in settings:
          db.session.add(ProfileSettings(profile_id=profile.id, setting_id=setting.id, value=setting.default))
        db.session.commit()
      except Exception as exc:
        log.error(exc, exc_info=True)
        profile = None
    # Initialise profile in InstaPy
    if profile:
      try:
          executor.worker_start(worker_id=profile.id, meta_data=profile.username, target_func=init_profile_in_instapy)
      except Exception as exc:
          log.error(exc, exc_info=True)
          # no need to set profile = None here
    return profile

def init_profile_in_instapy(username):
  try:
    session = InstaPy(username=username, password="")
    session.end()
  except Exception as exc:
    log.warning(exc, exc_info=True)



