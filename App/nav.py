from flask_nav import Nav
from dominate import tags
from flask_nav.renderers import Renderer
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator, RawTag, NavigationItem
from .database import db, Profile

# Main navigation object
nav = Nav()

def menu():
  profiles = Profile.query.filter_by(active=True).all()
  navbar = Navbar(
    'Title',
    View('Home', 'frontend.index', icon='home')
  )
  # Tools - only available if there's at least one profile
  if profiles:
    navbar.items.append(View('Tools', 'frontend.follower_following_tools', icon='flask'))
  navbar.items.append(View('Custom lists', 'frontend.custom_lists', icon='th-list'))
  navbar.items.append(View('Proxies', 'frontend.proxies', icon='plug'))
  navbar.items.append(View('Profiles', 'frontend.profiles', icon='users'))
  # List of profiles
  if profiles:
    navbar.items.append(Separator())
    profiles_wrapper = []
    if len(profiles) > 5:
      profiles_wrapper.append(build_profiles_search())
    for profile in profiles:
      profiles_wrapper.append(RawTag([Subgroup(
        View(profile.username, 'frontend.profile_view', profile_id=profile.id, icon='user'),
        View('Sessions', 'frontend.profile_sessions', profile_id=profile.id, icon='cubes'),
        View('Settings', 'frontend.profile_edit', profile_id=profile.id, icon='edit')
      )], _class='js-nav-profile-list-item'))
    navbar.items.append(RawTag(profiles_wrapper, _class='js-nav-profile-list'))

  return navbar

nav.register_element('menu', menu)

def build_profiles_search():
  search_wrap = tags.div(_class='md-form form-sm form-inline m-0')
  input = tags.input(_class='form-control form-control-sm mr-3 w-75', type='text', placeholder='Filter profiles')
  icon = tags.i(_class='fas fa-filter')
  search_wrap.add(input)
  search_wrap.add(icon)
  return RawTag(search_wrap)

## Renderers

@nav.renderer()
class NavRenderer(Renderer):
  def __init__(self):
    self.root_class = 'nav flex-column list-unstyled'
    self.link_class = 'nav-link'
    self.item_class = 'nav-item'
    self.text_class = 'nav-text'
    self.subgroup_class = 'card subgroup my-2 d-none d-lg-block'
    self.separator_class = 'separator mt-2'
    self.active_class = 'active'
  def visit_Navbar(self, node):
    #
    #  <ul class="self.root_class">
    #    <li class="self.item_class self.active_class">
    #     self.visit(item)
    #    </li>
    #  </ul>
    #
    if not node.items:
      return ''
    root_tag = tags.ul(_class=self.root_class)
    for item in node.items:
      _class = self.item_class
      if item.active:
        _class += ' ' + self.active_class
      item_tag = tags.li(self.visit(item), _class=_class)
      root_tag.add(item_tag)
    return root_tag
  def visit_Subgroup(self, node):
    #
    #  <div class="self.subgroup_class">
    #
    #    if node.title is RawTag:
    #     <span class="self.active_class">
    #       <i class="fas fa-{icon} mr-2"></i> node.title
    #     </span>
    #    else:
    #     node.title(class=pl-2 self.active_class)
    #
    #    <ul class="ml-2 list-unstyled">
    #      <li> subitem </li>
    #    </ul>
    #
    #  </div>
    #
    group = tags.ul(_class='m-0 ml-3 list-unstyled')
    if type(node.title) is RawTag:
      title = tags.span()
      if node.title.attribs:
        icon = node.title.attribs.pop('icon', None)
        if icon:
          title.appendChild(tags.i(_class='fas fa-{} mr-2'.format(icon)))
      title.add(node.title.content)
    else:
      title = self.visit(node.title)
      title.attributes['class'] += ' pl-2'
    if node.active:
      title.attributes['class'] += ' {}'.format(self.active_class)
    for item in node.items:
      group.add(tags.li(self.visit(item), _class=""))
    return tags.div(title, group, _class=self.subgroup_class)
  def visit_View(self, node):
    return self.visit_Link(node)
  def visit_Link(self, node):
    #
    #  <a href="node.get_url()" class="self.link_class self.active_class">
    #    <i class="fas fa-{icon} mr-2"></i> node.text
    #  </a>
    #
    _class = self.link_class
    if node.active:
      _class += ' ' + self.active_class
    anchor = tags.a('', _class=_class)
    if node.url_for_kwargs:
      icon = node.url_for_kwargs.pop('icon', None)
      if icon:
        anchor.appendChild(tags.i(_class='fas fa-{} mr-2'.format(icon)))
    anchor.add(self.visit(Text(node.text)))
    # Deffered setting the link because of url_for_kwargs
    anchor.set_attribute('href', node.get_url())
    return anchor
  def visit_Separator(self, node):
    #
    #  <div class="self.separator_class" ></div>
    #
    return tags.div(_class=self.separator_class)
  def visit_Text(self, node):
    #
    #  <span class="self.text_class"> {{ node.text }}</span>
    #
    return tags.span(node.text, _class=self.text_class)
  def visit_RawTag(self, node):
    # Overriden to be able to append tags
    content = node.content
    attribs = {}
    if node.attribs:
      attribs = node.attribs
    if type(content) is list:
      content = tags.div(**attribs)
      for item in node.content:
        content.add(self.visit(item))
    return content

@nav.renderer()
class SidebarRenderer(NavRenderer):
  def __init__(self):
    super(SidebarRenderer, self).__init__()
    self.root_class = 'list-group list-group-flush'
    self.link_class = 'list-group-item waves-effect'
    self.text_class = 'nav-text text-dark'
  def visit_Navbar(self, node):
    #
    #  <div class="self.root_class">
    #    self.visit(item)
    #  </div>
    #
    if not node.items:
      return ''
    root_tag = tags.div(_class=self.root_class)
    for item in node.items:
      root_tag.add(self.visit(item))
    return root_tag


@nav.renderer()
class NavBarRenderer(NavRenderer):
  def __init__(self):
    super(NavBarRenderer, self).__init__()
    self.root_class = 'navbar-nav mr-auto'


