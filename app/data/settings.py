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


class StageSetting:
    E_AFTER_START_TIMESLOT = "start-timeslot"
    E_AFTER_LOGON = "logon"

default_configuration_settings = {
    'stage-2-start-timer-at': (StageSetting.E_AFTER_START_TIMESLOT, Settings.SETTING_TYPE.E_STRING),
    'stage-2-delay': (0, Settings.SETTING_TYPE.E_INT),
    'stage-2-delay-start-timer-until-start-timeslot': (True, Settings.SETTING_TYPE.E_BOOL),
    'stage-3-start-timer-at': (StageSetting.E_AFTER_START_TIMESLOT, Settings.SETTING_TYPE.E_STRING),
    'stage-3-delay': (0, Settings.SETTING_TYPE.E_INT),
    'stage-3-delay-start-timer-until-start-timeslot': (True, Settings.SETTING_TYPE.E_BOOL),
    'timeslot-first-start': ('2021-2-10-14:0:0', Settings.SETTING_TYPE.E_STRING),
    'timeslot-length': (30, Settings.SETTING_TYPE.E_INT),
    'timeslot-number': (10, Settings.SETTING_TYPE.E_INT),
    'timeslot-max-guests': (50, Settings.SETTING_TYPE.E_INT),
}


def get_configuration_settings():
    configuration_settings = {}
    for k, v in default_configuration_settings.items():
        found, value = get_setting(k, 1)
        if found:
            configuration_settings[k] = value
        else:
            add_setting(k, v[0], v[1], 1)
            configuration_settings[k] = v[0]
    return configuration_settings


def set_configuration_setting(setting, value):
    if value == None:
        value = default_configuration_settings[setting][0]
    set_setting(setting, value, 1)