#
#=====================================
#
# THIS FILE IS DATABASE MIGRATOR APP STARTING POINT
#
#=====================================
#
#
from flask_migrate import Migrate
from ..create_app import create_app, ensure_app_dirs
from . import db, init_database

ensure_app_dirs()

app = create_app(__name__)

# Why provision (creating, stamping the db) should happen here:
# - This is basically the point where we create the DB
# - When this is called for the first time - from installer - before the app is run
# it will create database and stamp it with the latest version
# - For any other subsequent call it will be fine because db is already created
# and it has a stamp so we can perform migrations and upgrades
init_database(app)

migrate = Migrate(app, db, render_as_batch=True)



