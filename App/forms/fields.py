from flask_wtf import FlaskForm
from wtforms import Field, HiddenField, StringField, IntegerField, DecimalField, SubmitField, BooleanField, PasswordField, FieldList, FormField

class IHiddenField(StringField):
  def __init__(self, label='', validators=None, **kwargs):
    super(IHiddenField, self).__init__(label, validators, **kwargs)
    self.type = 'hidden'

class IStringField(StringField):
  def __init__(self, label='', validators=None, **kwargs):
    super(IStringField, self).__init__(label, validators, **kwargs)
    self.type = 'text'

class IPasswordField(StringField):
  def __init__(self, label='', validators=None, **kwargs):
    super(IPasswordField, self).__init__(label, validators, **kwargs)
    self.type = 'password'

class IIntegerField(StringField):
  def __init__(self, label='', validators=None,
    min=None, max=None, step=None,
    **kwargs):
    super(IIntegerField, self).__init__(label, validators, **kwargs)
    self.type = 'number'
    self.min = min
    self.max = max
    self.step = step

class IDecimalField(StringField):
  def __init__(self, label='', validators=None,
     min=None, max=None, step=None,
    **kwargs):
    super(IDecimalField, self).__init__(label, validators, **kwargs)
    self.type = 'number'
    self.min = min
    self.max = max
    self.step = step

class IBooleanField(StringField):
  def __init__(self, label='', validators=None, **kwargs):
    super(IBooleanField, self).__init__(label, validators, **kwargs)
    self.type = 'boolean'

class IFieldList(FieldList):
  def __init__(self, unbound_field, label='', validators=None,
    min_entries=None, **kwargs):
    super(IFieldList, self).__init__(unbound_field, label, validators, **kwargs)
    self.type = 'list'
  def clear(self):
    self.entries = []
    self.last_index = -1
  def append(self, entries):
    if entries:
      # Important - entries must be added one by one
      # Otherwise the entire list would be added as one entry
      for entry in entries:
        self.append_entry(entry)

class IObjectField(StringField):
  def __init__(self, label='', validators=None, **kwargs):
    super(IObjectField, self).__init__(label, validators, **kwargs)
    self.type = 'object'

def build_field(setting):
  switcher = {
    'object': IObjectField(),
    'text': IStringField(),
    'number': IIntegerField(),
    'decimal': IDecimalField(),
    'boolean': IBooleanField(),
    'list': IFieldList(IStringField())
  }
  return switcher.get(setting.data_type_key, None)