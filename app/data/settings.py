from flask_login import current_user
from app.data.models import Settings
from app import log
from app import db
import json


# return: found, value
# found: if True, setting was found else not
# value ; if setting was found, returns the value
def get_setting(name, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_INT:
            value = int(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_FLOAT:
            value = float(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = True if setting.value == 'True' else False
        else:
            value = setting.value
    except:
        return False, ''
    return True, value


def add_setting(name, value, type, id=-1):
    setting = Settings(name=name, value=str(value), type=type, user_id=id if id > -1 else current_user.id)
    db.session.add(setting)
    db.session.commit()
    log.info('add: {}'.format(setting.log()))
    return True


def set_setting(name, value, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = 'True' if value else 'False'
        setting.value = value
        db.session.commit()
    except:
        return False
    return True


def get_test_server():
    found, value = get_setting('test_server', 1)
    if found: return value
    add_setting('test_server', False, Settings.SETTING_TYPE.E_BOOL, 1)
    return False


default_configuration_settings = {
    'register-template': ('', Settings.SETTING_TYPE.E_STRING),
    'invite-mail-subject-template': ('', Settings.SETTING_TYPE.E_STRING),
    'invite-mail-content-template': ('', Settings.SETTING_TYPE.E_STRING),
    'register-mail-ack-subject-template': ('', Settings.SETTING_TYPE.E_STRING),
    'register-mail-ack-content-template': ('', Settings.SETTING_TYPE.E_STRING),

    'email-task-interval': (10, Settings.SETTING_TYPE.E_INT),
    'emails-per-minute': (30, Settings.SETTING_TYPE.E_INT),
    'email-send-max-retries': (2, Settings.SETTING_TYPE.E_INT),

    'base-url': ('localhost:5000', Settings.SETTING_TYPE.E_STRING),

    'enable-send-invite-email': (False, Settings.SETTING_TYPE.E_BOOL),
    'enable-send-ack-email': (False, Settings.SETTING_TYPE.E_BOOL),
    'enable-send-email': (False, Settings.SETTING_TYPE.E_BOOL),
}


def get_configuration_settings():
    configuration_settings = {}
    for k in default_configuration_settings:
        configuration_settings[k] = get_configuration_setting(k)
    return configuration_settings


def set_configuration_setting(setting, value):
    if None == value:
        value = default_configuration_settings[setting][0]
    return set_setting(setting, value, 1)


def get_configuration_setting(setting):
    found, value = get_setting(setting, 1)
    if found:
        return value
    else:
        default_setting = default_configuration_settings[setting]
        add_setting(setting, default_setting[0], default_setting[1], 1)
        return default_setting[0]


# save settings which are not in the database yet
# get_configuration_settings()