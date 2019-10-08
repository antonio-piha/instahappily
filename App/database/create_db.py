import os
import sys

# For InstaPy imports
sys.path.append("../..")
from InstaPy.instapy import database_engine as instapy_database

from ..settings import Settings, InstaPySettings
from ..logger import Logger
from .model import *
from flask_migrate import Migrate, stamp

log = Logger.get(__name__)

#
# Init database - purpose
# - to establish a connection with db
# - to create db in case the file is missing, or if it was never created before
# - flask-migrate is used to "stamp" the version to db - only if db is created
#
# Notes:
# - db represents both db's: app db and instapy db
# - flask-migrate's migrate or upgrade commands shouldn't be used here
# only stamping is allowed and only in case when the db is created
# - migrate command should always be used manually outside the code
# - upgrade command should be run from installers/updaters
# #
def init_database(app, provision=True):
  # We need to push app context for Db creation
  with app.app_context():
    try:
      # App DB
      db.init_app(app)
    except Exception as exc:
      log.error(exc, exc_info=True)
      return
    if not provision:
      return
    # Provision, verify, stamp
    app_database_created = False
    instapy_database_created = False
    try:
      if not os.path.isfile(Settings.database_location):
        app_database_created = True
        log.info("App database file not found")
        # The default bind (SQLALCHEMY_DATABASE_URI) is named None - this is the app DB
        db.create_all(bind=None)
        log.info("App database created")
        insert_initial_values()
      # Verify the data integrity after we're sure that db exists
    except Exception as exc:
      log.error(exc, exc_info=True)
    # Verify the db, in case of the error we can still stamp it
    try:
      verify_and_set_integrity()
    except Exception as exc:
      log.error(exc, exc_info=True)
    try:
      # InstaPy DB - make sure we have it
      if not os.path.isfile(InstaPySettings.database_location):
        instapy_database_created = True
        log.info("InstaPy database file not found - creating")
        instapy_database.get_database(make=True)
        log.info("InstaPy database created")
    except Exception as exc:
      log.error(exc, exc_info=True)
    # Stamp both db's - set alembic version for both
    try:
      # This will run only for the first time when both are created
      # If either one of them were created we need to stamp it
      # with the latest version
      # Stamp will ignore the one that is already stamped
      # But it will also stamp the latest version if the old one was present
      # Ideally stamping should happen only when both are created
      if app_database_created and instapy_database_created:
        migrate = Migrate(app, db, render_as_batch=True)
        stamp(directory=Settings.migrations_location)
    except Exception as exc:
      log.error(exc, exc_info=True)

# Initial DB data
initial_values_setting_group = [
  SettingGroup(key='likes'),
  SettingGroup(key='follow'),
  SettingGroup(key='unfollow'),
  SettingGroup(key='comments'),
  SettingGroup(key='relationship'),
  SettingGroup(key='interact'),
  SettingGroup(key='quota_supervisor'),
  SettingGroup(key='ignore'),
  SettingGroup(key='other'),
  SettingGroup(key='tool'),
  SettingGroup(key='system')
]

initial_values_setting_data_type = [
  SettingDataType(key='text'),
  SettingDataType(key='number'),
  SettingDataType(key='decimal'),
  SettingDataType(key='password'),
  SettingDataType(key='boolean'),
  SettingDataType(key='list'),
  SettingDataType(key='object')
]

initial_values_session_setting = [
  # Likes
  SessionSetting(group_key='likes', key='do_liking', data_type_key='boolean', default='False'),
  SessionSetting(group_key='likes', key='liking_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='likes', key='delimit_liking', data_type_key='boolean', default='False'),
  SessionSetting(group_key='likes', key='min_likes_per_post', data_type_key='number', default=''),
  SessionSetting(group_key='likes', key='max_likes_per_post', data_type_key='number', default=''),
  SessionSetting(group_key='likes', key='like_by_tags_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='likes', key='like_by_tags_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='likes', key='like_by_tags_amount', data_type_key='number', default='30'),
  SessionSetting(group_key='likes', key='like_by_tags_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='likes', key='like_by_user_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='likes', key='like_by_user_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='likes', key='like_by_user_amount', data_type_key='number', default='5'),
  SessionSetting(group_key='likes', key='like_by_user_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='likes', key='do_like_by_feed', data_type_key='boolean', default='False'),
  SessionSetting(group_key='likes', key='like_by_feed_amount', data_type_key='number', default='100'),
  SessionSetting(group_key='likes', key='like_by_feed_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='likes', key='like_by_locations_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='likes', key='like_by_locations_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='likes', key='like_by_locations_amount', data_type_key='number', default='10'),
  # Follow
  SessionSetting(group_key='follow', key='do_following', data_type_key='boolean', default='False'),
  SessionSetting(group_key='follow', key='follow_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='follow', key='follow_times', data_type_key='number', default='1'),
  SessionSetting(group_key='follow', key='follow_username_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_username_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_username_times', data_type_key='number', default='1'),
  SessionSetting(group_key='follow', key='follow_username_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='follow', key='follow_user_followers_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_user_followers_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_user_followers_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_user_followers_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='follow', key='follow_user_followers_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='follow', key='follow_user_following_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_user_following_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_user_following_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_user_following_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='follow', key='follow_user_following_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='follow', key='follow_by_tags_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_by_tags_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_by_tags_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_by_locations_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_by_locations_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_by_locations_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_by_tags_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='follow', key='follow_likers_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_likers_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_likers_photos_grab_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_likers_per_photo', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_likers_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='follow', key='follow_likers_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='follow', key='follow_commenters_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='follow', key='follow_commenters_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='follow', key='follow_commenters_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='follow', key='follow_commenters_daysold', data_type_key='number', default='365'),
  SessionSetting(group_key='follow', key='follow_commenters_max_pic', data_type_key='number', default='100'),
  SessionSetting(group_key='follow', key='follow_commenters_sleep_delay', data_type_key='number', default='600'),
  # Unfollow
  SessionSetting(group_key='unfollow', key='unfollow_custom_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='unfollow', key='unfollow_custom_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='unfollow', key='unfollow_custom_list_amount', data_type_key='number', default=''),
  SessionSetting(group_key='unfollow', key='unfollow_custom_list_track', data_type_key='text', default='all'),
  SessionSetting(group_key='unfollow', key='unfollow_custom_list_style', data_type_key='text', default='RANDOM'),
  SessionSetting(group_key='unfollow', key='unfollow_custom_list_unfollow_after', data_type_key='number', default='86400'),
  SessionSetting(group_key='unfollow', key='unfollow_custom_list_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='unfollow', key='do_unfollow_who_we_followed', data_type_key='boolean', default='False'),
  SessionSetting(group_key='unfollow', key='unfollow_who_we_followed_amount', data_type_key='number', default='60'),
  SessionSetting(group_key='unfollow', key='unfollow_who_we_followed_track', data_type_key='text', default='nonfollowers'),
  SessionSetting(group_key='unfollow', key='unfollow_who_we_followed_style', data_type_key='text', default='RANDOM'),
  SessionSetting(group_key='unfollow', key='unfollow_who_we_followed_unfollow_after', data_type_key='number', default='86400'),
  SessionSetting(group_key='unfollow', key='unfollow_who_we_followed_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='unfollow', key='do_unfollow_non_followers', data_type_key='boolean', default='False'),
  SessionSetting(group_key='unfollow', key='unfollow_non_followers_amount', data_type_key='number', default='60'),
  SessionSetting(group_key='unfollow', key='unfollow_non_followers_style', data_type_key='text', default='RANDOM'),
  SessionSetting(group_key='unfollow', key='unfollow_non_followers_unfollow_after', data_type_key='number', default='86400'),
  SessionSetting(group_key='unfollow', key='unfollow_non_followers_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='unfollow', key='do_unfollow_all_following', data_type_key='boolean', default='False'),
  SessionSetting(group_key='unfollow', key='unfollow_all_following_amount', data_type_key='number', default='60'),
  SessionSetting(group_key='unfollow', key='unfollow_all_following_style', data_type_key='text', default='RANDOM'),
  SessionSetting(group_key='unfollow', key='unfollow_all_following_unfollow_after', data_type_key='number', default='86400'),
  SessionSetting(group_key='unfollow', key='unfollow_all_following_sleep_delay', data_type_key='number', default='600'),
  SessionSetting(group_key='unfollow', key='dont_unfollow_my_active_users', data_type_key='boolean', default='False'),
  SessionSetting(group_key='unfollow', key='dont_unfollow_my_active_users_post_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='unfollow', key='like_by_feed_unfollow', data_type_key='boolean', default='False'),
  # Relationship
  SessionSetting(group_key='relationship', key='potency_ratio_followers_count', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='potency_ratio_following_count', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='potency_ratio_positivness', data_type_key='text', default='-'),
  SessionSetting(group_key='relationship', key='relationship_bounds_min_posts', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='relationship_bounds_max_posts', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='relationship_bounds_min_following', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='relationship_bounds_min_followers', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='relationship_bounds_max_following', data_type_key='number', default=''),
  SessionSetting(group_key='relationship', key='relationship_bounds_max_followers', data_type_key='number', default=''),
  # Comments
  SessionSetting(group_key='comments', key='do_commenting', data_type_key='boolean', default='False'),
  SessionSetting(group_key='comments', key='delimit_commenting', data_type_key='boolean', default='False'),
  SessionSetting(group_key='comments', key='delimit_commenting_min', data_type_key='number', default=''),
  SessionSetting(group_key='comments', key='delimit_commenting_max', data_type_key='number', default=''),
  SessionSetting(group_key='comments', key='delimit_commenting_mandatory_words', data_type_key='list', default='[]'),
  SessionSetting(group_key='comments', key='delimit_commenting_mandatory_words_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='comments', key='comment_by_locations_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='comments', key='comment_by_locations_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='comments', key='comment_by_locations_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='comments', key='commenting_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='comments', key='comments_general_all_media', data_type_key='list', default='[]'),
  SessionSetting(group_key='comments', key='comments_general_all_media_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='comments', key='comments_general_photo', data_type_key='list', default='[]'),
  SessionSetting(group_key='comments', key='comments_general_photo_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='comments', key='comments_general_video', data_type_key='list', default='[]'),
  SessionSetting(group_key='comments', key='comments_general_video_custom_list', data_type_key='object', default=''),
  # Interact
  SessionSetting(group_key='interact', key='user_interact_number_of_posts', data_type_key='number', default='5'),
  SessionSetting(group_key='interact', key='user_interact_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='interact', key='user_interact_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_by_users_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_by_users_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_by_users_amount', data_type_key='number', default='5'),
  SessionSetting(group_key='interact', key='interact_by_users_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_by_users_tagged_posts_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_by_users_tagged_posts_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_by_users_tagged_posts_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='interact', key='interact_by_users_tagged_posts_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_by_users_following_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_by_users_following_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_by_users_following_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='interact', key='interact_by_users_following_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_by_user_followers_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_by_user_followers_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_by_user_followers_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='interact', key='interact_by_user_followers_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_on_posts_at_url_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_on_posts_at_url_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_on_posts_at_url_randomize', data_type_key='boolean', default='True'),
  SessionSetting(group_key='interact', key='interact_on_posts_at_url_interact_owner', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='like_by_tags_interact', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='like_by_feed_interact', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='follow_by_username_list_interact', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_on_follow_user_followers', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_on_follow_user_following', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_on_follow_likers', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_on_follow_commenters', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_by_comments_users_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='interact', key='interact_by_comments_users_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='interact', key='interact_by_comments_posts_amount', data_type_key='number', default='10'),
  SessionSetting(group_key='interact', key='interact_by_comments_comments_per_post', data_type_key='number', default='5'),
  SessionSetting(group_key='interact', key='interact_by_comments_interact_commenters', data_type_key='boolean', default='False'),
  SessionSetting(group_key='interact', key='interact_by_comments_randomize', data_type_key='boolean', default='True'),
  # Ignore
  SessionSetting(group_key='ignore', key='ignore_users_by_user_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='ignore', key='ignore_users_by_user_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='ignore', key='exclude_friends_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='ignore', key='exclude_friends_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='ignore', key='skip_and_avoid_hashtags_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='ignore', key='skip_and_avoid_hashtags_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='ignore', key='ignore_skip_hashtags_if_contains_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='ignore', key='ignore_skip_hashtags_if_contains_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='ignore', key='skip_first_top_posts', data_type_key='boolean', default='False'),
  SessionSetting(group_key='ignore', key='skip_private', data_type_key='boolean', default='False'),
  SessionSetting(group_key='ignore', key='skip_private_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='ignore', key='skip_no_profile_pic', data_type_key='boolean', default='True'),
  SessionSetting(group_key='ignore', key='skip_no_profile_pic_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='ignore', key='skip_business', data_type_key='boolean', default='False'),
  SessionSetting(group_key='ignore', key='skip_business_percentage', data_type_key='number', default='1'),
  SessionSetting(group_key='ignore', key='skip_business_categories', data_type_key='list', default='[]'),
  SessionSetting(group_key='ignore', key='dont_skip_business_categories', data_type_key='list', default='[]'),
  # Other
  SessionSetting(group_key='other', key='do_like_by_smart_hashtags', data_type_key='boolean', default='False'),
  SessionSetting(group_key='other', key='do_follow_by_smart_hashtags', data_type_key='boolean', default='False'),
  SessionSetting(group_key='other', key='smart_hashtags_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='other', key='smart_hashtags_custom_list', data_type_key='object', default=''),
  SessionSetting(group_key='other', key='smart_hashtags_limit', data_type_key='number', default='10'),
  SessionSetting(group_key='other', key='smart_hashtags_sort', data_type_key='text', default='random'),
  SessionSetting(group_key='other', key='run_forever', data_type_key='boolean', default='False'),
  SessionSetting(group_key='other', key='use_clarifai', data_type_key='boolean', default='False'),
  SessionSetting(group_key='other', key='clarifai_api_key', data_type_key='text', default=''),
  # Tools
  SessionSetting(group_key='tool', key='follower_following_tool_type', data_type_key='text', default=''),
  SessionSetting(group_key='tool', key='follower_following_tool_target_user_list', data_type_key='list', default='[]'),
  SessionSetting(group_key='tool', key='follower_following_tool_grab_amount', data_type_key='number', default='100'),
  SessionSetting(group_key='tool', key='follower_following_tool_unfollowers_compare_by', data_type_key='text', default='latest'),
  SessionSetting(group_key='tool', key='follower_following_tool_unfollowers_compare_track', data_type_key='text', default='first')
]

initial_values_profile_setting = [
  # Quota supervisor
  ProfileSetting(group_key='quota_supervisor', key='do_quota_supervise', data_type_key='boolean', default='True'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_sleep_after_list', data_type_key='list', default='[]'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_sleepyhead', data_type_key='boolean', default='True'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_stochastic_flow', data_type_key='boolean', default='True'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_likes_hourly', data_type_key='number', default='100'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_likes_daily', data_type_key='number', default=''),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_comments_hourly', data_type_key='number', default='17'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_comments_daily', data_type_key='number', default=''),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_follows_hourly', data_type_key='number', default='100'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_follows_daily', data_type_key='number', default=''),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_unfollows_hourly', data_type_key='number', default='100'),
  ProfileSetting(group_key='quota_supervisor', key='quota_supervisor_peak_unfollows_daily', data_type_key='number', default=''),
  ProfileSetting(group_key='other', key='clarifai_api_key', data_type_key='text', default='')
]

initial_values_app_settings = [
  AppSetting(group_key='system', key='settings_view_level', data_type_key='text', default='simple'),
  AppSetting(group_key='system', key='serial_key_hash', data_type_key='text', default=''),
]

initial_values_custom_list_type = [
  CustomListType(key='usernames'),
  CustomListType(key='hashtags'),
  CustomListType(key='comments'),
  CustomListType(key='locations'),
  CustomListType(key='links')
]


## Functions
############################################################################################
def insert_initial_values():
  initials = [
    initial_values_setting_group,
    initial_values_setting_data_type,
    initial_values_session_setting,
    initial_values_profile_setting,
    initial_values_app_settings,
    initial_values_custom_list_type
  ]
  try:
    for initial in initials:
      for entity in initial:
        db.session.add(entity)
      db.session.commit()
    log.info('App database initialized with values')
  except Exception as exc:
    log.error(exc, exc_info=True)


def populate_base(existing_data, initial_values, matching_criteria_callable, returnable_object):
  to_commit = False
  for initial_value in initial_values:
    already_in = False
    for existing_row in existing_data:
      if matching_criteria_callable(initial_value, existing_row):
        already_in = True
        break
    if not already_in:
      db.session.add(returnable_object(initial_value))
      to_commit = True
  if to_commit:
    db.session.commit()

def populate_by_key(existing_data, initial_values):
  populate_base(existing_data, initial_values,
    matching_criteria_callable=lambda i, e: i.key == e.key,
    returnable_object=lambda i: i
  )

def populate_settings(existing_data, initial_values, returnable_object):
  populate_base(existing_data, initial_values, returnable_object=returnable_object,
    matching_criteria_callable=lambda i, e: i.key == e.setting.key
  )

def verify_and_set_integrity():

  try:
    populate_by_key(existing_data=SettingDataType.query.all(), initial_values=initial_values_setting_data_type)
    populate_by_key(existing_data=SettingGroup.query.all(), initial_values=initial_values_setting_group)
    populate_by_key(existing_data=SessionSetting.query.all(), initial_values=initial_values_session_setting)
    populate_by_key(existing_data=ProfileSetting.query.all(), initial_values=initial_values_profile_setting)
    populate_by_key(existing_data=AppSetting.query.all(), initial_values=initial_values_app_settings)
    populate_by_key(existing_data=CustomListType.query.all(), initial_values=initial_values_custom_list_type)
  except Exception as exc:
    log.error(exc, exc_info=True)

  try:
    # Sessions settings - needs to traverse sessions one by one
    sessions = Session.query.all()
    initial_values = SessionSetting.query.all()
    for session in sessions:
      existing_settings = session.settings
      populate_settings(existing_settings, initial_values,
        returnable_object=lambda i: SessionSettings(session_id=session.id, setting_id=i.id, value=i.default)
      )
    # Profiles settings - needs to traverse profiles one by one
    profiles = Profile.query.all()
    initial_values = ProfileSetting.query.all()
    for profile in profiles:
      existing_settings = profile.settings
      populate_settings(existing_settings, initial_values,
        returnable_object=lambda i: ProfileSettings(profile_id=profile.id, setting_id=i.id, value=i.default)
      )
    # App settings
    existing_settings = AppSettings.query.all()
    initial_values = AppSetting.query.all()
    populate_settings(existing_settings, initial_values,
      returnable_object=lambda i: AppSettings(setting_key=i.key, value=i.default)
    )
    log.info("App database integrity verified and set")
  except Exception as exc:
    log.error(exc, exc_info=True)


