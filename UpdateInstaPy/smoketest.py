import sys

# For InstaPy imports
sys.path.append("..")
from InstaPy.instapy import InstaPy
from InstaPy.proxy_extension import create_proxy_extension
from InstaPy.instapy.util import smart_run
import App.settings

# login credentials
insta_username = 'taninuyar'
insta_password = 'mojpassword123'

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False)

with smart_run(session):
    """ Activity flow """
    # general settings
    session.set_relationship_bounds(enabled=True,
                                    delimit_by_numbers=True,
                                    max_followers=4590,
                                    min_followers=45,
                                    min_following=77)

    session.set_dont_include(["friend1", "friend2", "friend3"])
    session.set_dont_like(["pizza", "#store"])

    # activity
    session.like_by_tags(["natgeo"], amount=10)