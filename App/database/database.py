import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from ..logger import Logger

log = Logger.get(__name__)

password_magic_word_if_stored = '!2£1Password3Stored4Successfully5$5_'

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

try:
  db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
except Exception as exc:
  log.error(exc, exc_info=True)


