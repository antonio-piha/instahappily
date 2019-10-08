import json
from flask import Blueprint, render_template, flash, redirect, url_for, escape, request
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
from .database import db, Profile, Session, SessionSetting, AppSettings, AppSetting, Proxy, FollowerFollowingToolRequestResult, CustomList
from .service import DataService, SessionService, ProfileService, FollowerFollowingToolService, CustomListService
from .view_model import *
from .session import SessionRepository
from .follower_following_tool import FollowerFollowingToolRepository
from .forms import *
from .logger import Logger

log = Logger.get(__name__)

blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def index():
  # Counters
  counters = {'profiles': 0, 'sessions': 0, 'custom_lists': 0, 'tool_requests': 0 }
  try:
    counters['profiles'] = Profile.query.count()
    counters['sessions'] = Session.query.filter_by(is_system=False).count()
    counters['custom_lists'] = CustomList.query.filter_by(is_system=False).count()
    counters['tool_requests'] = FollowerFollowingToolRequestResult.query.filter_by(is_system=False).count()
    counters['proxies'] = Proxy.query.count()
  except Exception as exc:
    log.error(exc, exc_info=True)
  # Sessions, proxies
  sessions = []
  try:
    sessions = Session.query.filter(Session.active==True, Session.is_system==False).all()
    sessions_with_proxy_enabled = SessionRepository.filter_sessions_with_proxy_enabled(sessions)
  except Exception as exc:
    log.error(exc, exc_info=True)
  return render_template('home.jinja2', counters=counters,
    sessions=sessions, sessions_with_proxy_enabled=sessions_with_proxy_enabled)

# Profile
@blueprint.route('/add-profile', methods=['GET', 'POST'])
def profile_add():
  form = ProfileAddForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      username = form.username.data
      existing_profile = Profile.query.filter_by(username=username).first()
      if not existing_profile:
        profile = ProfileService.create_profile(username=username, plain_password=form.password.data)
        if profile == None:
          flash('Profile {} can\'t be added right now becuase something went wrong. Please try again'.format(escape(username)), 'danger')
        else:
          flash('Profile {} successfully added'.format(escape(username)), 'success')
          return redirect('/profile/{}/edit'.format(profile.id))
      else:
        flash('Profile {} already exists.'.format(username), 'warning')
  return render_template('profile_add.jinja2', form=form)

@blueprint.route('/profiles', methods=['GET'])
def profiles():
  profiles = Profile.query.filter_by(active=True).all()
  deactivated_profiles = Profile.query.filter_by(active=False).all()
  profile_activate_form = ProfileActivateForm()
  profile_deactivate_form = ProfileDeactivateForm()
  return render_template('profiles.jinja2', profiles=profiles, deactivated_profiles=deactivated_profiles,
    profile_activate_form=profile_activate_form, profile_deactivate_form=profile_deactivate_form
    )

@blueprint.route('/profile/<int:profile_id>', methods=['GET'])
def profile_view(profile_id):
  profile = Profile.query.filter_by(id=profile_id).first()
  profile_deactivate_form = ProfileDeactivateForm()
  profile_activate_form = ProfileActivateForm()
  if profile is None:
    flash("That profile doesn't exist. Please add new profile.")
    return redirect('/add-profile')
  activity_record = ProfileService.get_profile_activity_records(profile)
  return render_template('profile_view.jinja2', profile=profile, activity_record=activity_record,
    profile_deactivate_form=profile_deactivate_form, profile_activate_form=profile_activate_form)

@blueprint.route('/profile/<int:profile_id>/edit', methods=['GET', 'POST'])
def profile_edit(profile_id):
  profile = Profile.query.filter_by(id=profile_id).first()
  if profile is None or not profile:
    flash("That profile doesn't exist. Please add new profile.")
    return redirect('/add-profile')
  form = ProfileEditForm()
  profile_deactivate_form = ProfileDeactivateForm()
  profile_activate_form = ProfileActivateForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      profile.save(plain_password=form.password.data, proxy_id=form.proxy_id.data)
      DataService.save_profile_settings_from_view_model(
        profile = profile,
        profile_settings_view_model = form.to_view_model()
      )
      flash('Profile {} successfully saved'.format(escape(profile.username)), 'success')
      form.proxy_id.data = profile.proxy_id
  else:
    # Refresh the forms
    form.set_from_view_model(ProfileSettingsViewModel().set_from_model(profile.settings))
    form.proxy_id.data = profile.proxy_id
  # Just to ensure the real password is not returned
  form.password.data = password_magic_word_if_stored
  return render_template('profile_edit.jinja2', profile=profile, form=form,
    profile_deactivate_form=profile_deactivate_form, profile_activate_form=profile_activate_form)

@blueprint.route('/profile/<int:profile_id>/sessions', methods=['GET', 'POST'])
def profile_sessions(profile_id):
  profile = Profile.query.filter_by(id=profile_id).first()
  if profile is None:
    flash("That profile doesn't exist. Please add new profile.")
    return redirect('/add-profile')
  session_add_form = SessionAddForm()
  session_duplicate_form = SessionDuplicateForm()
  session_activate_form = SessionActivateForm()
  session_deactivate_form = SessionDeactivateForm()
  action_all_sessions_for_profile = ActionAllSessionsForProfile()
  session_start_form = SessionStartForm()
  session_stop_form = SessionStopForm()
  session_add_form.profile_id.data = profile_id
  sessions = Session.query.filter(Session.profile_id==profile_id, Session.active==True, Session.is_system==False).all()
  deactivated_sessions = Session.query.filter(Session.profile_id==profile_id, Session.active==False, Session.is_system==False).all()
  return render_template('profile_sessions.jinja2', profile=profile, sessions=sessions,
    deactivated_sessions=deactivated_sessions,
    session_add_form=session_add_form, session_duplicate_form=session_duplicate_form,
    session_deactivate_form=session_deactivate_form, session_start_form=session_start_form,
    session_stop_form=session_stop_form, session_activate_form=session_activate_form,
    action_all_sessions_for_profile=action_all_sessions_for_profile)

@blueprint.route('/profile/<int:profile_id>/activate', methods=['POST'])
def profile_activate(profile_id):
  form = ProfileActivateForm()
  if form.validate_on_submit():
    profile = Profile.query.filter_by(id=profile_id).first()
    if profile is None:
      flash("That profile doesn't exist. Please add new profile.")
      return redirect('/add-profile')
    profile.activate()
    flash('Profile {} successfully activated'.format(escape(profile.username)), 'success')
    return redirect('/profile/{}/edit'.format(profile.id))
  return redirect('/deactivated-profiles')

@blueprint.route('/profile/<int:profile_id>/deactivate', methods=['POST'])
def profile_dectivate(profile_id):
  form = ProfileDeactivateForm()
  if form.validate_on_submit():
    profile = Profile.query.filter_by(id=profile_id).first()
    if profile is None:
      flash("That profile doesn't exist. Please add new profile.")
      return redirect('/add-profile')
    # Session must stop first
    stop = SessionService.stop_multiple_sessions(profile.sessions)
    if stop:
      profile.deactivate()
      flash('Profile {} successfully deactivated'.format(escape(profile.username)), 'success')
    else:
      flash('Profile session can\'t stop. Please try again.', 'danger')
  return redirect('/deactivated-profiles')

@blueprint.route('/profile/<int:profile_id>/all-sessions/<action>', methods=['POST'])
def action_all_sessions_for_profile(profile_id, action):
  form = ActionAllSessionsForProfile()
  if form.validate_on_submit():
    profile = Profile.query.filter_by(id=profile_id).first()
    if profile is None:
      flash("That profile doesn't exist. Please add new profile.")
      return redirect('/add-profile')
    sessions = Session.query.filter(Session.profile_id==profile_id, Session.active==True, Session.is_system==False).all()
    if action == 'start':
      SessionService.start_multiple_sessions(sessions)
      flash('{} sessions successfully started'.format(escape(profile.username)), 'success')
    if action == 'stop':
      SessionService.stop_multiple_sessions(sessions)
      flash('{} sessions successfully stopped'.format(escape(profile.username)), 'success')
    if action == 'restart':
      SessionService.restart_multiple_sessions(sessions)
      flash('{} sessions successfully restarted'.format(escape(profile.username)), 'success')
  return redirect('/profile/{}/sessions'.format(profile.id))

# Session

@blueprint.route('/session/add', methods=['GET', 'POST'])
def session_add():
  form = SessionAddForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      session = SessionRepository.create_session(name=form.name.data, profile_id=form.profile_id.data)
      if session:
        flash('Session {} successfully created'.format(escape(session.name)), 'success')
        return redirect('/session/{}/settings'.format(session.id))
      else:
        flash('Something went wrong. Session wasn\'t created. Please try again.', 'danger')
  return render_template('session_add.html', form=form)

@blueprint.route('/session/<int:session_id>/duplicate', methods=['POST'])
def session_duplicate(session_id):
  form = SessionDuplicateForm()
  if form.validate_on_submit():
    session = SessionRepository.duplicate_session(session_id=session_id)
    if session:
      flash('Session successfully duplicated', 'success')
      return redirect('/session/{}/settings'.format(session.id))
    else:
      flash('Something went wrong. Session wasn\'t duplicated. Please try again.', 'danger')
  return redirect('/session/{}/settings'.format(session_id))

@blueprint.route('/session/<int:session_id>/start', methods=['POST'])
def session_run(session_id):
  form = SessionStartForm()
  if form.validate_on_submit():
    run = SessionService.start_session(session_id)
    if run:
      flash('Session successfully started', 'success')
    else:
      flash('Session can\'t start. Please try again.', 'danger')
  return redirect('/session/{}/settings'.format(session_id))

@blueprint.route('/session/<int:session_id>/stop', methods=['POST'])
def session_stop(session_id):
  form = SessionStopForm()
  if form.validate_on_submit():
    stop = SessionService.stop_session(session_id)
    if stop:
      flash('Session successfully stopped', 'success')
    else:
      flash('Session can\'t stop. Please try again.', 'danger')
  return redirect('/session/{}/settings'.format(session_id))

@blueprint.route('/session/<int:session_id>/settings', methods=['GET', 'POST'])
def session_settings(session_id):
  session = Session.query.filter_by(id=session_id).first()
  if session is None:
    flash("That session doesn't exist. Please add new session.")
    return redirect('/session/add')
  profile = session.profile
  if profile is None:
    flash("That session is not attached to profile which is not allowed. Please attach this session to one profile.")
    return redirect('/session/add')
  session_deactivate_form = SessionDeactivateForm()
  session_activate_form = SessionActivateForm()
  session_duplicate_form = SessionDuplicateForm()
  session_start_form = SessionStartForm()
  session_stop_form = SessionStopForm()
  form = SessionSettingsForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      session_settings, view_model = SessionRepository.save_session_settings(
        session = session,
        session_settings_view_model = form.to_view_model()
      )
      form.set_from_view_model(view_model)
      flash('Session saved successfully.', 'success')
      restart = request.form.get('restart')
      if restart:
        restart = SessionService.restart_session(session_id)
        if restart:
          flash('Session restarted successfully.', 'success')
        else:
          flash('Session failed to restart.', 'danger')
    else:
      flash('Some session settings are wrong. Please check.', 'danger')
  else:
    # Refresh the forms
    view_model = SessionSettingsViewModel().set_from_model(session.settings)
    view_model.session_name = session.name
    form.set_from_view_model(view_model)
  custom_lists_sorted_by_type = CustomListService.get_custom_lists_for_display()
  return render_template('session_settings.jinja2', session=session, profile=profile, form=form,
    session_start_form=session_start_form, session_stop_form=session_stop_form,
    session_activate_form=session_activate_form, session_deactivate_form=session_deactivate_form, session_duplicate_form=session_duplicate_form,
    custom_lists_sorted_by_type=custom_lists_sorted_by_type)

@blueprint.route('/session/<int:session_id>/activate', methods=['POST'])
def session_activate(session_id):
  form = SessionActivateForm()
  if form.validate_on_submit():
    session = Session.query.filter_by(id=session_id).first()
    if session is None:
      flash("That session doesn't exist. Please add new session.")
      return redirect('/session/add')
    session.activate()
    flash('Session successfully activated', 'success')
    return redirect('/session/{}/settings'.format(session.id))
  return redirect('/profile/{}/sessions'.format(session.profile_id))

@blueprint.route('/session/<int:session_id>/deactivate', methods=['POST'])
def session_dectivate(session_id):
  form = SessionDeactivateForm()
  if form.validate_on_submit():
    session = Session.query.filter_by(id=session_id).first()
    if session is None:
      flash("That session doesn't exist. Please add new session.")
      return redirect('/session/add')
    # Session must stop first
    stop = SessionService.stop_session(session_id)
    if stop:
      session.deactivate()
      flash('Session successfully deactivated', 'success')
    else:
      flash('Session currently can\'t be stopped or deactivated. Please try again.', 'danger')
  return redirect('/profile/{}/sessions'.format(session.profile_id))

# Proxy
@blueprint.route('/add-proxy', methods=['GET', 'POST'])
def proxy_add():
  form = ProxyAddForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      view_model = form.to_view_model()
      existing_proxy = Proxy.query.filter(Proxy.ip==view_model.ip,Proxy.port==view_model.port).first()
      if not existing_proxy:
        proxy = Proxy()
        proxy.create(
          name=view_model.name,
          ip=view_model.ip,
          port=view_model.port,
          username=view_model.username,
          plain_password=view_model.password,
          active=True
        )
        if proxy == None:
          flash('Proxy {} can\'t be added right now becuase something went wrong. Please try again'.format(escape(proxy.name)), 'danger')
        else:
          flash('Proxy {} successfully added'.format(escape(proxy.name)), 'success')
          return redirect('/proxies')
      else:
        flash('Proxy {}:{} already exists. Saved under name {}'.format(existing_proxy.ip, existing_proxy.port, existing_proxy.name), 'warning')
  return render_template('proxy_add.jinja2', form=form)

@blueprint.route('/proxies', methods=['GET'])
def proxies():
  proxies = Proxy.query.filter_by(active=True).all()
  deactivated_proxies = Proxy.query.filter_by(active=False).all()
  proxy_activate_form = ProxyActivateForm()
  proxy_deactivate_form = ProxyDeactivateForm()
  proxies_profiles = {}
  all_proxies = []
  all_proxies.extend(proxies)
  all_proxies.extend(deactivated_proxies)
  profiles = Profile.query.filter_by(active=True).all()
  for proxy in all_proxies:
    proxies_profiles[proxy.id] = [p for p in profiles if p.proxy_id == proxy.id]
  return render_template('proxies.jinja2', proxies=proxies, proxies_profiles=proxies_profiles,
    deactivated_proxies=deactivated_proxies, proxy_activate_form=proxy_activate_form,
    proxy_deactivate_form=proxy_deactivate_form
    )

@blueprint.route('/proxy/<int:proxy_id>/edit', methods=['GET', 'POST'])
def proxy_edit(proxy_id):
  proxy = Proxy.query.filter_by(id=proxy_id).first()
  if proxy is None or not proxy:
    flash("That proxy doesn't exist. Please add new proxy.")
    return redirect('/add-proxy')
  form = ProxyEditForm()
  proxy_activate_form = ProxyActivateForm()
  proxy_deactivate_form = ProxyDeactivateForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      view_model = form.to_view_model()
      proxy.save(
        name=view_model.name,
        ip=view_model.ip,
        port=view_model.port,
        username=view_model.username,
        plain_password=view_model.password,
        active=proxy.active
      )
      flash('Proxy {} successfully saved'.format(escape(proxy.name)), 'success')
  else:
    # Refresh the forms
    form.set_from_view_model(ProxyViewModel().set_from_model(proxy))
    # Just to ensure the real password is not returned
  form.password.data = password_magic_word_if_stored
  return render_template('proxy_edit.jinja2', form=form, proxy=proxy,
    proxy_activate_form=proxy_activate_form, proxy_deactivate_form=proxy_deactivate_form)

@blueprint.route('/proxy/<int:proxy_id>/activate', methods=['POST'])
def proxy_activate(proxy_id):
  form = ProxyActivateForm()
  if form.validate_on_submit():
    proxy = Proxy.query.filter_by(id=proxy_id).first()
    if proxy is None:
      flash("That proxy doesn't exist. Please add new proxy.")
      return redirect('/add-proxy')
    proxy.activate()
    flash('Proxy {} successfully activated'.format(escape(proxy.name)), 'success')
    return redirect('/proxy/{}/edit'.format(proxy.id))
  return redirect('/proxies')

@blueprint.route('/proxy/<int:proxy_id>/deactivate', methods=['POST'])
def proxy_dectivate(proxy_id):
  form = ProxyDeactivateForm()
  if form.validate_on_submit():
    proxy = Proxy.query.filter_by(id=proxy_id).first()
    if proxy is None:
      flash("That proxy doesn't exist. Please add new proxy.")
      return redirect('/add-proxy')
    proxy.deactivate()
    flash('Proxy {} successfully deactivated'.format(escape(proxy.name)), 'success')
  return redirect('/proxies')


# App Settings

@blueprint.route('/app-settings', methods=['GET', 'POST'])
def app_settings():
  app_settings = AppSettings.query.all()
  form = AppSettingsForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      DataService.save_app_settings_from_view_model(
        app_settings_view_model = form.to_view_model()
      )
      flash('App settings saved successfully.', 'success')
    else:
      flash('Some app settings are wrong.', 'danger')
  else:
    form.set_from_view_model(AppSettingsViewModel().set_from_model(app_settings))
  return render_template('app_settings.jinja2', form=form)

@blueprint.route('/app-settings-defaults', methods=['GET', 'POST'])
def app_settings_defaults():
  app_settings_defaults = AppSetting.query.all()
  form = AppSettingsForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      DataService.save_app_settings_defaults_from_view_model(
        app_settings_defaults_view_model = form.to_view_model()
      )
      flash('App settings defaults saved successfully.', 'success')
    else:
      flash('Some app settings defaults are wrong.', 'danger')
  else:
    form.set_from_view_model(AppSettingsDefaultsViewModel().set_from_model(app_settings_defaults))
  return render_template('app_settings.jinja2', form=form)

@blueprint.route('/session-settings-defaults', methods=['GET', 'POST'])
def session_settings_defaults():
  session_settings_defaults = SessionSetting.query.all()
  form = SessionSettingsDefaultsForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      DataService.save_session_settings_defaults_from_view_model(
        session_settings_defaults_view_model = form.to_view_model()
      )
      flash('Session settings defaults saved successfully.', 'success')
    else:
      flash('Some session settings defaults are wrong.', 'danger')
  else:
    form.set_from_view_model(SessionSettingsDefaultsViewModel().set_from_model(session_settings_defaults))
  return render_template('session_settings_defaults.jinja2', form=form)

# Tools

@blueprint.route('/follower-following-tools', methods=['GET', 'POST'])
def follower_following_tools():
  form = FollowerFollowingToolForm()
  actions_form = ActionAllFollowerFollowingToolForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      created_request = FollowerFollowingToolService.create_request_from_view_model(form.to_view_model())
      if created_request:
        flash('Request successfully created and started', 'success')
        # clear the form - so far only possible by doing redirect
        return redirect('/follower-following-tools')
      else:
        flash('Something went wrong. Please try again.', 'danger')
    else:
      flash('Some requests settings are wrong.', 'danger')
  if form.follower_following_tool_grab_amount.data == '' or form.follower_following_tool_grab_amount.data == None:
    form.follower_following_tool_grab_amount.data = 100
  previous_requests = FollowerFollowingToolService.get_requests()
  return render_template('follower_following_tools.jinja2', form=form, previous_requests=previous_requests,
    actions_form=actions_form)

@blueprint.route('/follower-following-tools/request/<int:request_id>/start', methods=['POST'])
def follower_following_tools_request_start(request_id):
  form = ActionAllFollowerFollowingToolForm()
  if form.validate_on_submit():
    run = FollowerFollowingToolService.start_request(request_id)
    if run:
      flash('Request successfully started', 'success')
    else:
      flash('Request can\'t start. Please try again.', 'danger')
  return redirect('/follower-following-tools')

@blueprint.route('/follower-following-tools/request/<int:request_id>/stop', methods=['POST'])
def follower_following_tools_request_stop(request_id):
  form = ActionAllFollowerFollowingToolForm()
  if form.validate_on_submit():
    run = FollowerFollowingToolService.stop_request(request_id)
    if run:
      flash('Request successfully stopped', 'success')
    else:
      flash('Request can\'t stop. Please try again.', 'danger')
  return redirect('/follower-following-tools')

@blueprint.route('/follower-following-tools/request/<int:request_id>/edit', methods=['GET', 'POST'])
def follower_following_tools_request_edit(request_id):
  tool_request = FollowerFollowingToolRequestResult.query.filter_by(id=request_id).first()
  if tool_request is None:
    flash("That request doesn't exist. Please add a new one.")
    return redirect('/follower-following-tools')
  form = FollowerFollowingToolForm()
  actions_form = ActionAllFollowerFollowingToolForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      saved = FollowerFollowingToolService.save_request_from_view_model(tool_request, form.to_view_model())
      if saved:
        flash('Request successfully saved', 'success')
      else:
        flash('Request can\'t be saved. Please try again.', 'danger')
  else:
    # Refresh the form
    form.set_from_view_model(FollowerFollowingToolViewModel().set_from_model(tool_request))
  display_info = FollowerFollowingToolService.from_request_to_display_info(tool_request)
  return render_template('follower_following_tools_request_edit.jinja2', form=form,
    tool_request=tool_request, actions_form=actions_form, display_info=display_info)


# Custom lists

@blueprint.route('/custom-lists', methods=['GET', 'POST'])
def custom_lists():
  form = CustomListAddForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      created_list = CustomListService.create_custom_list_from_view_model(form.to_view_model())
      if created_list:
        flash('Custom list successfully created.', 'success')
        # clear the form - so far only possible by doing redirect
        return redirect('/custom-lists')
      else:
        flash('Something went wrong. Please try again.', 'danger')
    else:
      flash('Some fields are wrong.', 'danger')
  custom_lists = CustomList.query.filter_by(active=True, is_system=False).all()
  return render_template('custom_lists.jinja2', form=form, custom_lists=custom_lists)

@blueprint.route('/custom-lists/<int:custom_list_id>/edit', methods=['GET', 'POST'])
def custom_list_edit(custom_list_id):
  custom_list = CustomList.query.filter_by(id=custom_list_id).first()
  if custom_list is None:
    flash("That custom list doesn't exist. Please add a new one.")
    return redirect('/custom-lists')
  form = CustomListAddForm()
  #actions_form = ActionAllFollowerFollowingToolForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      saved = CustomListService.save_custom_list_from_view_model(custom_list, form.to_view_model())
      if saved:
        flash('Custom list successfully saved', 'success')
        return redirect('/custom-lists/{}/edit'.format(custom_list.id))
      else:
        flash('Custom list can\'t be saved. Please try again.', 'danger')
  else:
    # Refresh the form
    form.set_from_view_model(CustomListViewModel().set_from_model(custom_list))
  return render_template('custom_lists_edit.jinja2', form=form, custom_list=custom_list)




############################################################################
# Error handlers
############################################################################

def handle_bad_request(exc):
  page = index()
  #flash('Unfortunately bad request happened and you got redirected to homepage.', 'danger')
  log.error(exc, exc_info=True)
  return page, BadRequest.code

def handle_internal_server_error(exc):
  page = index()
  #flash('Unfortunately something bad happened and you got redirected to homepage. This error will be reported and fixed. Please try again what you were initially trying do to.', 'danger')
  log.error(exc, exc_info=True)
  return page, InternalServerError.code

def handle_not_found_error(exc):
  page = index()
  #flash('I can\'t find the thing you\'re looking for so you got redirected to homepage.', 'danger')
  return page, NotFound.code

def init_app(app):
  app.register_blueprint(blueprint)
  app.register_error_handler(BadRequest.code, handle_bad_request)
  app.register_error_handler(InternalServerError.code, handle_internal_server_error)
  app.register_error_handler(NotFound.code, handle_not_found_error)

