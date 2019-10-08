import sys
import signal
import atexit
import logging
import random
import json
from datetime import datetime
from InstaPy.instapy import InstaPy
from InstaPy.proxy_extension import create_proxy_extension
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from ..create_app import create_app
from ..database import db, init_database
from ..utils.custom_exceptions import SessionException
from ..logger import Logger
from ..settings import Settings
from .session_meta import SessionMeta
from .session_repository import SessionRepository
from ..follower_following_tool import FollowerFollowingToolResult, FollowerFollowingToolRepository

## Don't initialise log in this module, every session will have it's own log
# log = Logger.get(__name__)

app = None
# log - app logger - will log to app.log
log = None
# logger - session logger - will log to this profile instapy log
logger = None

session=None
session_meta=None
settings=None
exceptions=None

# This is the starting point in the child process started from Worker
# _session_meta is depickled from parent and this object is sent across processes
def start_session(_session_meta):
  global app, log, logger, session, settings, session_meta, exceptions
  # _session_meta is coming from parent process
  # so let's create clean object from it
  session_meta = SessionMeta().set_from_previous(_session_meta)
  #########################
  # App and DB connection #
  #########################

  app = create_app(__name__)
  with app.app_context():
    # No need to provision the db here, just init
    init_database(app, provision=False)

  log = Logger.get('Session.{}'.format(session_meta.session_id))

  #################
  # setup session #
  #################

  # Load from DB
  with app.app_context():
    session_meta = SessionRepository.populate_session_meta(session_meta)

  # DEBUG POINT
  # log.debug(json.dumps(session_meta.settings, default=lambda o: o.__dict__, sort_keys=True, indent=4))
  # exit()

  session = None
  try:
    settings = session_meta.settings

    # Resolve proxy
    proxy_address, proxy_port, proxy_chrome_extension = resolve_proxy(session_meta)

    # Create session object
    # - Make sure to use proper browser, and not headless browser - https://antoinevastel.com/bot%20detection/2018/01/17/detect-chrome-headless-v2.html
    session = InstaPy(username=session_meta.username,
      password=session_meta.passwords['profile'],
      headless_browser=False,
      proxy_address=proxy_address,
      proxy_port=proxy_port,
      proxy_chrome_extension=proxy_chrome_extension,
      disable_image_load=True,
      bypass_suspicious_attempt=True,
      bypass_with_mobile=True,
      show_logs=False # To avoid creating StreamHandler on the logger
      )
    logger = session.logger
    adjust_session_logger(logger_filter=session_meta.logger_filter)
  except Exception as exc:
    log.error(exc, exc_info=True)
    session = None

  # If something went wrong, no reason to continue
  if not session:
    return

  ###############
  # run session #
  ###############
  workload_function = session_meta.workload_function
  if workload_function is None or not callable(workload_function):
    workload_function = session_workload

  while True:
    # Try inside a while to be able to rerun in case of error
    should_break = False
    try:
      exceptions = []
      session_start()

      # Really important part
      ########################
      ### LOGIN STARTS HERE
      ########################
      session.login()

      workload_function()
    except NoSuchElementException as exc:
      # if changes to IG layout
      browser = session.browser.page_source.encode('utf8')
      log.error("{} **-**-**-**-** Browser page_source: {}".format(exc, browser), exc_info=True)
      # In this case break from the loop, there's no point to continue
      should_break = True
    except WebDriverException as exc:
      log.error(exc, exc_info=True)
      # Can't recover from this one - could be that browser process died
      should_break = True
    except SessionException as exc:
      handle_session_exceptions(exc)
    except Exception as exc:
      log.error(exc, exc_info=True)
    finally:
      # This will try to re-run in successful finish but not in the case when exception happens within the process
      if should_break or not session_meta.run_forever:
        # end the bot session
        session_end()
        break

    #############
    # After this line session will end (and the process)
    #############

def handle_session_exceptions(exc):
  # TODO Implement feedback to user on errors around sessions
  for sub_exc in exc.exceptions:
    log.error(sub_exc, exc_info=True)

def session_start():
  try:
    # Session
    session_model = session_meta.session
    if session_model:
      session_model.start_datetime = datetime.now()
      with app.app_context():
        db.session.add(session_model)
        db.session.commit()
  except Exception as exc:
    log.error(exc, exc_info=True)

def session_end():
  try:
    # InstaPy session object
    if session:
      session.end()
    # Session model (DB object)
    session_model = session_meta.session
    if session_model:
      session_model.end_datetime = datetime.now()
      with app.app_context():
        db.session.add(session_model)
        db.session.commit()
  except Exception as exc:
    log.error(exc, exc_info=True)

# when this process exit
# atexit.register(session_end)

def resolve_proxy(session_meta):
  proxy_address=None
  proxy_port=None
  proxy_chrome_extension=None
  if session_meta.proxy:
    # TODO: Notify user: This session has a proxy attached but the proxy maybe deactivated
    if session_meta.proxy.active:
      # Check if we need to use authentication or not - check based only on username, if populated we need auth
      if session_meta.proxy.username is not None and session_meta.proxy.username != '':
        proxy = '{}:{}@{}:{}'.format(session_meta.proxy.username, session_meta.passwords['proxy'], session_meta.proxy.ip, session_meta.proxy.port)
        proxy_chrome_extension = create_proxy_extension(proxy)
      else:
        proxy_address = session_meta.proxy.ip
        # in this case port must be an int
        proxy_port = int(session_meta.proxy.port) if session_meta.proxy.port is not None and session_meta.proxy.port != '' else None
  return (proxy_address,proxy_port,proxy_chrome_extension)

def adjust_session_logger(logger_filter):
  global logger
  # refer to InstaPy function get_instapy_logger
  original_session_formatter = None
  # Replace all InstaPy log handlers with our own
  # so far InstaPY is creating only one file handler per session
  # and one StreamHandler if show_logs session param is true
  for handler in logger.logger.handlers:
    if isinstance(handler, logging.FileHandler):
      # just take the last one
      original_session_formatter = handler.formatter
    logger.logger.removeHandler(handler)
  our_log_file_handler = Logger.get_file_handler()
  # Leave the original formater (because it shows username)
  our_log_file_handler.setFormatter(original_session_formatter)
  logger.logger.addHandler(our_log_file_handler)
  # Add our filter to the session logger.logger
  if logger_filter not in logger.logger.filters:
    logger.logger.addFilter(logger_filter)
  # Redirect print output to the same log file
  stdout_redirect_file = Settings.log_file
  sys.stdout = open(stdout_redirect_file, 'a')
  logger.debug('Redirected session stdout to {}'.format(stdout_redirect_file))

def session_work_unit(func, func_kwargs, condition_to_run=True):
  session_logger = SessionWorkUnitLogger(additional_prefix='[{}]'.format(func.__name__))
  result = None
  try:
    session_logger.debug('Begin')
    if condition_to_run:
      session_logger.debug('Args: {}'.format(json.dumps(func_kwargs)))
      ###################
      result = func(**func_kwargs)
      ###################
      session_logger.debug('Finished')
    else:
      session_logger.debug('Skipped')
  except WebDriverException:
    raise
  except Exception as exc:
    session_logger.exception(exc)
    exceptions.append(exc)
    result = None
  finally:
    session_logger.debug('End')
    return result

class SessionWorkUnitLogger:
  def __init__(self, additional_prefix=''):
    self.log_prefix = '_SF_ [{}] {}'.format(session_meta.session_id, additional_prefix)
  def info(self, msg):
    logger.info('{} {}'.format(self.log_prefix, msg))
  def debug(self, msg):
    logger.debug('{} {}'.format(self.log_prefix, msg))
  def exception(self, exc):
    # Must be warning level here because we'll log on error level outside the caller
    logger.warning(exc, exc_info=True)

# Functions that will carry the workload of sessions
# Defined as functions because they have to be accessible from subprocesses
#######################################################

def session_workload():
  # ooooooooooooooooooooooooooooooooooooooooo
  # Settings
  # ooooooooooooooooooooooooooooooooooooooooo

  try:
    skip_and_avoid_hashtags_list = list(set([] + settings.skip_and_avoid_hashtags_list + settings.skip_and_avoid_hashtags_custom_list))
  except Exception as exc:
    exceptions.append(exc)

  # set_do_like
  session_work_unit(
    condition_to_run=settings.do_liking,
    func=session.set_do_like,
    func_kwargs={
      'enabled' : settings.do_liking,
      'percentage' : SessionRepository.get_percentage(settings.liking_percentage)
    }
  )

  # set_do_comment
  session_work_unit(
    func=session.set_do_comment,
    func_kwargs={
      'enabled' : settings.do_commenting,
      'percentage' : SessionRepository.get_percentage(settings.commenting_percentage)
    }
  )

  # set_comments
  try:
    comments_general_all_media = list(set([] + settings.comments_general_all_media + settings.comments_general_all_media_custom_list))
    session_work_unit(
      condition_to_run=comments_general_all_media,
      func=session.set_comments,
      func_kwargs={
        'comments' : comments_general_all_media
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  try:
    comments_general_photo = list(set([] + settings.comments_general_photo + settings.comments_general_photo_custom_list))
    session_work_unit(
      condition_to_run=comments_general_photo,
      func=session.set_comments,
      func_kwargs={
        'comments' : comments_general_photo,
        'media' : 'Photo'
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  try:
    comments_general_video = list(set([] + settings.comments_general_video + settings.comments_general_video_custom_list))
    session_work_unit(
      condition_to_run=comments_general_video,
      func=session.set_comments,
      func_kwargs={
        'comments' : comments_general_video,
        'media' : 'Video'
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_do_follow
  session_work_unit(
    func=session.set_do_follow,
    func_kwargs={
      'enabled' : settings.do_following,
      'percentage' : SessionRepository.get_percentage(settings.follow_percentage),
      'times' : settings.follow_times
    }
  )

  # set_dont_unfollow_active_users
  session_work_unit(
    condition_to_run=settings.dont_unfollow_my_active_users,
    func=session.set_dont_unfollow_active_users,
    func_kwargs={
      'enabled' : settings.dont_unfollow_my_active_users,
      'posts' : settings.dont_unfollow_my_active_users_post_amount,
      'boundary' : 300
    }
  )

  # set_relationship_bounds
  try:
    followers_count = SessionRepository.optional(settings.potency_ratio_followers_count)
    following_count = SessionRepository.optional(settings.potency_ratio_following_count)
    relationship_bounds_enabled_by_potency_ratio = True if followers_count and following_count else False
    relationship_bounds_delimit_by_numbers = True if (
        SessionRepository.optional(settings.relationship_bounds_min_posts) or
        SessionRepository.optional(settings.relationship_bounds_max_posts) or
        SessionRepository.optional(settings.relationship_bounds_min_followers) or
        SessionRepository.optional(settings.relationship_bounds_max_followers) or
        SessionRepository.optional(settings.relationship_bounds_min_following) or
        SessionRepository.optional(settings.relationship_bounds_max_following)
      ) else False
    potency_ratio = None
    if relationship_bounds_enabled_by_potency_ratio:
      followers_count = round(abs(followers_count))
      following_count = round(abs(following_count))
      if settings.potency_ratio_positivness == '-':
        potency_ratio = round(following_count / followers_count)
        potency_ratio = -1 * potency_ratio
      if settings.potency_ratio_positivness == '+':
        potency_ratio = round(followers_count / following_count)
    session_work_unit(
      condition_to_run=relationship_bounds_enabled_by_potency_ratio or relationship_bounds_delimit_by_numbers,
      func=session.set_relationship_bounds,
      func_kwargs={
        'enabled' : relationship_bounds_enabled_by_potency_ratio or relationship_bounds_delimit_by_numbers,
        'potency_ratio' : potency_ratio,
        'delimit_by_numbers' : relationship_bounds_delimit_by_numbers,
        'min_posts' : SessionRepository.optional(settings.relationship_bounds_min_posts),
        'max_posts' : SessionRepository.optional(settings.relationship_bounds_max_posts),
        'max_followers' : SessionRepository.optional(settings.relationship_bounds_max_followers),
        'max_following' : SessionRepository.optional(settings.relationship_bounds_max_following),
        'min_followers' : SessionRepository.optional(settings.relationship_bounds_min_followers),
        'min_following' : SessionRepository.optional(settings.relationship_bounds_min_following)
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_smart_hashtags
  try:
    smart_hashtags_list = list(set([] + settings.smart_hashtags_list + settings.smart_hashtags_custom_list))
    session_work_unit(
      condition_to_run=smart_hashtags_list,
      func=session.set_smart_hashtags,
      func_kwargs={
        'tags' : smart_hashtags_list,
        'limit' : settings.smart_hashtags_limit,
        'sort' : settings.smart_hashtags_sort,
        'log_tags' : True
      }
    )
    if smart_hashtags_list and skip_and_avoid_hashtags_list:
      # Filter out ones we don't want
      session.smart_hashtags = [tag for tag in session.smart_hashtags if tag not in skip_and_avoid_hashtags_list]
  except Exception as exc:
    exceptions.append(exc)

  # set_skip_users
  session_work_unit(
    func=session.set_skip_users,
    func_kwargs={
      'skip_private' : settings.skip_private,
      'private_percentage' : SessionRepository.get_percentage(settings.skip_private_percentage),
      'skip_no_profile_pic' : settings.skip_no_profile_pic,
      'no_profile_pic_percentage' : SessionRepository.get_percentage(settings.skip_no_profile_pic_percentage),
      'skip_business' : settings.skip_business,
      'business_percentage' : SessionRepository.get_percentage(settings.skip_business_percentage),
      'skip_business_categories' : settings.skip_business_categories,
      'dont_skip_business_categories' : settings.dont_skip_business_categories
    }
  )

  # set_delimit_liking
  session_work_unit(
    func=session.set_delimit_liking,
    func_kwargs={
      'enabled' : settings.delimit_liking,
      'max' : SessionRepository.optional(settings.max_likes_per_post),
      'min' : SessionRepository.optional(settings.min_likes_per_post)
    }
  )

  # set_delimit_commenting
  try:
    delimit_commenting_mandatory_words = list(set([] + settings.delimit_commenting_mandatory_words + settings.delimit_commenting_mandatory_words_custom_list))
    enable_delimit_commenting = settings.delimit_commenting or len(delimit_commenting_mandatory_words) > 0
    # Issues with getting comments count
    session_work_unit(
      func=session.set_delimit_commenting,
      func_kwargs={
        'enabled' : enable_delimit_commenting,
        'max' : SessionRepository.optional(settings.delimit_commenting_max),
        'min' : SessionRepository.optional(settings.delimit_commenting_min),
        'comments_mandatory_words' : delimit_commenting_mandatory_words
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_dont_like
  # List is defined above (combination list with custom lists)
  session_work_unit(
    condition_to_run=skip_and_avoid_hashtags_list,
    func=session.set_dont_like,
    func_kwargs={
      'tags' : skip_and_avoid_hashtags_list
    }
  )

  # set_ignore_users
  try:
    ignore_users_by_user_list = list(set([] + settings.ignore_users_by_user_list + settings.ignore_users_by_user_custom_list))
    session_work_unit(
      condition_to_run=ignore_users_by_user_list,
      func=session.set_ignore_users,
      func_kwargs={
        'users' : ignore_users_by_user_list
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_ignore_if_contains
  try:
    ignore_skip_hashtags_if_contains_list = list(set([] + settings.ignore_skip_hashtags_if_contains_list + settings.ignore_skip_hashtags_if_contains_custom_list))
    session_work_unit(
      condition_to_run=ignore_skip_hashtags_if_contains_list,
      func=session.set_ignore_if_contains,
      func_kwargs={
        'words' : ignore_skip_hashtags_if_contains_list
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_dont_include
  try:
    exclude_friends_list = list(set([] + settings.exclude_friends_list + settings.exclude_friends_custom_list))
    session_work_unit(
      condition_to_run=exclude_friends_list,
      func=session.set_dont_include,
      func_kwargs={
        'friends' : exclude_friends_list
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # set_user_interact
  session_work_unit(
    func=session.set_user_interact,
    func_kwargs={
      'amount' : settings.user_interact_number_of_posts,
      'percentage' : SessionRepository.get_percentage(settings.user_interact_percentage),
      'randomize' : settings.user_interact_randomize,
      'media' : None
    }
  )

  # set_quota_supervisor
  session_work_unit(
    condition_to_run=settings.do_quota_supervise,
    func=session.set_quota_supervisor,
    func_kwargs={
      'enabled' : settings.do_quota_supervise,
      'sleep_after' : settings.quota_supervisor_sleep_after_list,
      'sleepyhead' : settings.quota_supervisor_sleepyhead,
      'stochastic_flow' : settings.quota_supervisor_stochastic_flow,
      'notify_me' : False,
      'peak_likes' : (
        SessionRepository.optional(settings.quota_supervisor_peak_likes_hourly),
        SessionRepository.optional(settings.quota_supervisor_peak_likes_daily)
      ),
      'peak_comments' : (
        SessionRepository.optional(settings.quota_supervisor_peak_comments_hourly),
        SessionRepository.optional(settings.quota_supervisor_peak_comments_daily)
      ),
      'peak_follows' : (
        SessionRepository.optional(settings.quota_supervisor_peak_follows_hourly),
        SessionRepository.optional(settings.quota_supervisor_peak_follows_daily)
      ),
      'peak_unfollows' : (
        SessionRepository.optional(settings.quota_supervisor_peak_unfollows_hourly),
        SessionRepository.optional(settings.quota_supervisor_peak_unfollows_daily)
      ),
      'peak_server_calls' : (None, None)
    }
  )

  # Clarifai disabled
  # set_use_clarifai
  # session_work_unit(
  #   condition_to_run=False,
  #   func=session.set_use_clarifai,
  #   func_kwargs={
  #     'enabled' : settings.use_clarifai,
  #     'api_key' : settings.clarifai_api_key
  #   }
  # )

  # ooooooooooooooooooooooooooooooooooooooooo
  # Actions
  # ooooooooooooooooooooooooooooooooooooooooo

  # like_by_users
  session_work_unit(
    condition_to_run=settings.like_by_user_list,
    func=session.like_by_users,
    func_kwargs={
      'usernames' : settings.like_by_user_list,
      'amount' : settings.like_by_user_amount,
      'randomize' : settings.like_by_user_randomize,
      'media' : None
    }
  )

  # comment_by_locations
  try:
    comment_by_locations_list = list(set([] + settings.comment_by_locations_list + settings.comment_by_locations_custom_list))
    session_work_unit(
      condition_to_run=comment_by_locations_list,
      func=session.comment_by_locations,
      func_kwargs={
        'locations' : comment_by_locations_list,
        'amount' : settings.comment_by_locations_amount,
        'media' : None,
        'skip_top_posts' : settings.skip_first_top_posts
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_by_list
  try:
    follow_username_list = list(set([] + settings.follow_username_list + settings.follow_username_custom_list))
    session_work_unit(
      condition_to_run=follow_username_list,
      func=session.follow_by_list,
      func_kwargs={
        'followlist' : follow_username_list,
        'times' : settings.follow_username_times,
        'sleep_delay' : settings.follow_username_sleep_delay,
        'interact' : settings.follow_by_username_list_interact
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_user_followers
  try:
    follow_user_followers_list = list(set([] + settings.follow_user_followers_list + settings.follow_user_followers_custom_list))
    session_work_unit(
      condition_to_run=follow_user_followers_list,
      func=session.follow_user_followers,
      func_kwargs={
        'usernames' : follow_user_followers_list,
        'amount' : settings.follow_user_followers_amount,
        'randomize' : settings.follow_user_followers_randomize,
        'interact' : settings.interact_on_follow_user_followers,
        'sleep_delay' : settings.follow_user_followers_sleep_delay
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_user_following
  try:
    follow_user_following_list = list(set([] + settings.follow_user_following_list + settings.follow_user_following_custom_list))
    session_work_unit(
      condition_to_run=follow_user_following_list,
      func=session.follow_user_following,
      func_kwargs={
        'usernames' : follow_user_following_list,
        'amount' : settings.follow_user_following_amount,
        'randomize' : settings.follow_user_following_randomize,
        'interact' : settings.interact_on_follow_user_following,
        'sleep_delay' : settings.follow_user_following_sleep_delay
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_by_tags
  try:
    follow_by_tags_list = list(set([] + settings.follow_by_tags_list + settings.follow_by_tags_custom_list))
    session_work_unit(
      condition_to_run=follow_by_tags_list,
      func=session.follow_by_tags,
      func_kwargs={
        'tags' : follow_by_tags_list,
        'amount' : settings.follow_by_tags_amount,
        'skip_top_posts' : settings.skip_first_top_posts,
        'use_smart_hashtags' : False,
        'randomize' : False,
        'media' : None
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_by_tags by smart_hashtags
  session_work_unit(
    condition_to_run=smart_hashtags_list and settings.do_follow_by_smart_hashtags,
    func=session.follow_by_tags,
    func_kwargs={
      'tags' : None,
      'amount' : settings.follow_by_tags_amount,
      'skip_top_posts' : settings.skip_first_top_posts,
      'use_smart_hashtags' : settings.do_follow_by_smart_hashtags,
      'randomize' : False,
      'media' : None
    }
  )

  # follow_likers
  try:
    follow_likers_list = list(set([] + settings.follow_likers_list + settings.follow_likers_custom_list))
    session_work_unit(
      condition_to_run=follow_likers_list,
      func=session.follow_likers,
      func_kwargs={
        'usernames' : follow_likers_list,
        'photos_grab_amount' : settings.follow_likers_photos_grab_amount,
        'follow_likers_per_photo' : settings.follow_likers_per_photo,
        'randomize' : settings.follow_likers_randomize,
        'sleep_delay' : settings.follow_likers_sleep_delay,
        'interact' : settings.interact_on_follow_likers
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_commenters
  try:
    follow_commenters_list = list(set([] + settings.follow_commenters_list + settings.follow_commenters_custom_list))
    session_work_unit(
      condition_to_run=follow_commenters_list,
      func=session.follow_commenters,
      func_kwargs={
        'usernames' : follow_commenters_list,
        'amount' : settings.follow_commenters_amount,
        'daysold' : settings.follow_commenters_daysold,
        'max_pic' : settings.follow_commenters_max_pic,
        'sleep_delay' : settings.follow_commenters_sleep_delay,
        'interact' : settings.interact_on_follow_commenters
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # follow_by_locations
  try:
    follow_by_locations_list = list(set([] + settings.follow_by_locations_list + settings.follow_by_locations_custom_list))
    session_work_unit(
      condition_to_run=follow_by_locations_list,
      func=session.follow_by_locations,
      func_kwargs={
        'locations' : follow_by_locations_list,
        'amount' : settings.follow_by_locations_amount,
        'media' : None,
        'skip_top_posts' : settings.skip_first_top_posts
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_by_users
  try:
    interact_by_users_list = list(set([] + settings.interact_by_users_list + settings.interact_by_users_custom_list))
    session_work_unit(
      condition_to_run=interact_by_users_list,
      func=session.interact_by_users,
      func_kwargs={
        'usernames' : interact_by_users_list,
        'amount' : settings.interact_by_users_amount,
        'randomize' : settings.interact_by_users_randomize,
        'media' : None
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_by_users_tagged_posts
  try:
    interact_by_users_tagged_posts_list = list(set([] + settings.interact_by_users_tagged_posts_list + settings.interact_by_users_tagged_posts_custom_list))
    session_work_unit(
      condition_to_run=interact_by_users_tagged_posts_list,
      func=session.interact_by_users_tagged_posts,
      func_kwargs={
        'usernames' : interact_by_users_tagged_posts_list,
        'amount' : settings.interact_by_users_tagged_posts_amount,
        'randomize' : settings.interact_by_users_tagged_posts_randomize,
        'media' : None
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_user_following
  try:
    interact_by_users_following_list = list(set([] + settings.interact_by_users_following_list + settings.interact_by_users_following_custom_list))
    session_work_unit(
      condition_to_run=interact_by_users_following_list,
      func=session.interact_user_following,
      func_kwargs={
        'usernames' : interact_by_users_following_list,
        'amount' : settings.interact_by_users_following_amount,
        'randomize' : settings.interact_by_users_following_randomize
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_user_followers
  try:
    interact_by_user_followers_list = list(set([] + settings.interact_by_user_followers_list + settings.interact_by_user_followers_custom_list))
    session_work_unit(
      condition_to_run=interact_by_user_followers_list,
      func=session.interact_user_followers,
      func_kwargs={
        'usernames' : interact_by_user_followers_list,
        'amount' : settings.interact_by_user_followers_amount,
        'randomize' : settings.interact_by_user_followers_randomize
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_by_URL
  try:
    interact_on_posts_at_url_list = list(set([] + settings.interact_on_posts_at_url_list + settings.interact_on_posts_at_url_custom_list))
    session_work_unit(
      condition_to_run=interact_on_posts_at_url_list,
      func=session.interact_by_URL,
      func_kwargs={
        'urls' : interact_on_posts_at_url_list,
        'randomize' : settings.interact_on_posts_at_url_randomize,
        'interact' : settings.interact_on_posts_at_url_interact_owner
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # interact_by_comments
  try:
    interact_by_comments_users_list = list(set([] + settings.interact_by_comments_users_list + settings.interact_by_comments_users_custom_list))
    session_work_unit(
      condition_to_run=interact_by_comments_users_list,
      func=session.interact_by_comments,
      func_kwargs={
        'usernames' : interact_by_comments_users_list,
        'posts_amount' : settings.interact_by_comments_posts_amount,
        'comments_per_post' : settings.interact_by_comments_comments_per_post,
        'reply' : False,
        'interact' : settings.interact_by_comments_interact_commenters,
        'randomize' : settings.interact_by_comments_randomize,
        'media' : None
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # unfollow_users by unfollow_custom_list
  try:
    unfollow_custom_list = list(set([] + settings.unfollow_custom_list + settings.unfollow_custom_custom_list))
    session_work_unit(
      condition_to_run=unfollow_custom_list,
      func=session.unfollow_users,
      func_kwargs={
        'amount' : SessionRepository.optional(settings.unfollow_custom_list_amount),
        'customList' : (True, unfollow_custom_list, settings.unfollow_custom_list_track),
        'style' : settings.unfollow_custom_list_style,
        'unfollow_after' : settings.unfollow_custom_list_unfollow_after,
        'sleep_delay' : settings.unfollow_custom_list_sleep_delay
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # unfollow_users by unfollow_who_we_followed
  session_work_unit(
    condition_to_run=settings.do_unfollow_who_we_followed,
    func=session.unfollow_users,
    func_kwargs={
      'amount' : settings.unfollow_who_we_followed_amount,
      'InstapyFollowed' : (True, settings.unfollow_who_we_followed_track),
      'style' : settings.unfollow_who_we_followed_style,
      'unfollow_after' : settings.unfollow_who_we_followed_unfollow_after,
      'sleep_delay' : settings.unfollow_who_we_followed_sleep_delay
    }
  )

  # unfollow_users by unfollow_non_followers
  session_work_unit(
    condition_to_run=settings.do_unfollow_non_followers,
    func=session.unfollow_users,
    func_kwargs={
      'amount' : settings.unfollow_non_followers_amount,
      'nonFollowers' : settings.do_unfollow_non_followers,
      'style' : settings.unfollow_non_followers_style,
      'unfollow_after' : settings.unfollow_non_followers_unfollow_after,
      'sleep_delay' : settings.unfollow_non_followers_sleep_delay
    }
  )

  # unfollow_users by unfollow_all_following
  session_work_unit(
    condition_to_run=settings.do_unfollow_all_following,
    func=session.unfollow_users,
    func_kwargs={
      'amount' : settings.unfollow_all_following_amount,
      'allFollowing' : settings.do_unfollow_all_following,
      'style' : settings.unfollow_all_following_style,
      'unfollow_after' : settings.unfollow_all_following_unfollow_after,
      'sleep_delay' : settings.unfollow_all_following_sleep_delay
    }
  )

  # like_by_locations
  try:
    like_by_locations_list = list(set([] + settings.like_by_locations_list + settings.like_by_locations_custom_list))
    session_work_unit(
      condition_to_run=like_by_locations_list,
      func=session.like_by_locations,
      func_kwargs={
        'locations' : like_by_locations_list,
        'amount' : settings.like_by_locations_amount,
        'media' : None,
        'skip_top_posts' : settings.skip_first_top_posts
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # like_by_tags
  try:
    like_by_tags_list = list(set([] + settings.like_by_tags_list + settings.like_by_tags_custom_list))
    if like_by_tags_list:
      random.shuffle(like_by_tags_list)
    session_work_unit(
      condition_to_run=like_by_tags_list,
      func=session.like_by_tags,
      func_kwargs={
        'tags' : like_by_tags_list,
        'amount' : settings.like_by_tags_amount,
        'skip_top_posts' : settings.skip_first_top_posts,
        'use_smart_hashtags' : False,
        'interact' : settings.like_by_tags_interact,
        'randomize' : settings.like_by_tags_randomize,
        'media' : None
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  # like_by_tags by _smart_hashtags
  session_work_unit(
    condition_to_run=smart_hashtags_list and settings.do_like_by_smart_hashtags,
    func=session.like_by_tags,
    func_kwargs={
      'tags' : None,
      'amount' : settings.like_by_tags_amount,
      'skip_top_posts' : settings.skip_first_top_posts,
      'use_smart_hashtags' : settings.do_like_by_smart_hashtags,
      'interact' : settings.like_by_tags_interact,
      'randomize' : False,
      'media' : None
    }
  )

  # like_by_feed
  session_work_unit(
    condition_to_run=settings.do_like_by_feed,
    func=session.like_by_feed,
    func_kwargs={
      'amount' : settings.like_by_feed_amount,
      'randomize' : settings.like_by_feed_randomize,
      'unfollow' : settings.like_by_feed_unfollow,
      'interact' : settings.like_by_feed_interact
    }
  )

  # like_by_users
  try:
    like_by_user_list = list(set([] + settings.like_by_user_list + settings.like_by_user_custom_list))
    session_work_unit(
      condition_to_run=like_by_user_list,
      func=session.like_by_users,
      func_kwargs={
        'usernames' : like_by_user_list,
        'amount' : settings.like_by_user_amount,
        'randomize' : settings.like_by_user_randomize
      }
    )
  except Exception as exc:
    exceptions.append(exc)

  ############################################################
  # End of session workload
  ############################################################
  # Raise all gathered exceptions as one
  if exceptions:
    raise SessionException(exceptions)




# Tools
#######################################################################################################################################


def session_follower_following_tool():
  try:
    session_logger = SessionWorkUnitLogger(additional_prefix='[follower_following_tool]')
    amount = settings.follower_following_tool_grab_amount
    amount = 'full' if amount == '' or amount == None else int(amount)
    result = FollowerFollowingToolResult()

    if not settings.follower_following_tool_target_user_list:
      session_logger.debug('Skipping: list follower_following_tool_target_user_list is empty')
      save_tools_result(result)
      return

    # Targeted users must be traversed here because we need to merge results
    for targeted_user in settings.follower_following_tool_target_user_list:

      # grab_followers
      result_grab_followers = session_work_unit(
        condition_to_run=settings.follower_following_tool_type == 'followers',
        func=session.grab_followers,
        func_kwargs={
          'username' : targeted_user,
          'amount' : amount,
          'live_match' : False,
          'store_locally' : True
        }
      )
      if result_grab_followers:
        result.followers.update(result_grab_followers)

      # grab_following
      result_grab_followings = session_work_unit(
        condition_to_run=settings.follower_following_tool_type == 'followings',
        func=session.grab_following,
        func_kwargs={
          'username' : targeted_user,
          'amount' : amount,
          'live_match' : False,
          'store_locally' : True
        }
      )
      if result_grab_followings:
        result.followings.update(result_grab_followings)

      # pick_unfollowers
      # To be able to pick unfollowers we need to generate followers data
      if (settings.follower_following_tool_type == 'all_unfollowers'
        or
        settings.follower_following_tool_type == 'active_unfollowers'):
        # and important part is to store it in local storage
        result_grab_followers = session_work_unit(
          condition_to_run=True,
          func=session.grab_followers,
          func_kwargs={
            'username' : targeted_user,
            'amount' : 'full',
            'live_match' : False,
            'store_locally' : True
          }
        )
        # Now pick unfollowers
        result_pick_unfollowers = session_work_unit(
          condition_to_run=True,
          func=session.pick_unfollowers,
          func_kwargs={
            'username' : targeted_user,
            'compare_by' : settings.follower_following_tool_unfollowers_compare_by,
            'compare_track' : settings.follower_following_tool_unfollowers_compare_track,
            'live_match' : False,
            'store_locally' : True,
            'print_out' : False
          }
        )
        if result_pick_unfollowers:
          all_unfollowers, active_unfollowers = result_pick_unfollowers
          if all_unfollowers:
            result.all_unfollowers.update(all_unfollowers)
          if active_unfollowers:
            result.active_unfollowers.update(active_unfollowers)

      # pick_nonfollowers
      result_pick_nonfollowers = session_work_unit(
        condition_to_run=settings.follower_following_tool_type == 'nonfollowers',
        func=session.pick_nonfollowers,
        func_kwargs={
          'username' : targeted_user,
          'live_match' : False,
          'store_locally' : True
        }
      )
      if result_pick_nonfollowers:
        result.nonfollowers.update(result_pick_nonfollowers)

      # pick_fans
      result_pick_fans = session_work_unit(
        condition_to_run=settings.follower_following_tool_type == 'fans',
        func=session.pick_fans,
        func_kwargs={
          'username' : targeted_user,
          'live_match' : False,
          'store_locally' : True
        }
      )
      if result_pick_fans:
        result.fans.update(result_pick_fans)

      # pick_mutual_following
      result_pick_mutual_following = session_work_unit(
        condition_to_run=settings.follower_following_tool_type == 'mutual_following',
        func=session.pick_mutual_following,
        func_kwargs={
          'username' : targeted_user,
          'live_match' : False,
          'store_locally' : True
        }
      )
      if result_pick_mutual_following:
        result.mutual_following.update(result_pick_mutual_following)
  except Exception as exc:
    session_logger.exception(exc)
    exceptions.append(exc)

  # Save result
  result = result if not exceptions else '_FAILED_'
  saved = save_tools_result(result)
  if not saved:
    exceptions.append(Exception('Failed to save FollowerFollowingTools result.'))

  # Raise all gathered exceptions as one
  if exceptions:
    raise SessionException(exceptions)

def save_tools_result(result):
  # Save result to DB
  saved = False
  with app.app_context():
    saved = FollowerFollowingToolRepository.save_result_by_session(session_meta.session_id, result)
  return saved

