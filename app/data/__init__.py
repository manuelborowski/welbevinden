from app import flask_app, login_manager
from app.data.user import load_user as user_load_user


@flask_app.before_first_request
def at_start():
    pass
    # db_subject_topic.add_default_values_if_empty()
    # db_measure_topic.add_default_values_if_empty()

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return user_load_user(user_id)


__all__ = ['models', 'settings', 'user', 'utils', 'student']


import app.data.models
import app.data.settings
import app.data.student
import app.data.utils
import app.data.survey
import app.data.user
