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

stage_settings_config = [
    ('stage-2', (
        ('start-timer-at', StageSetting.E_AFTER_START_TIMESLOT, Settings.SETTING_TYPE.E_STRING),
        ('delay', 0, Settings.SETTING_TYPE.E_INT),
        ('delay-start-timer-until-start-timeslot', True, Settings.SETTING_TYPE.E_BOOL),
    )),
    ('stage-3', (
        ('start-timer-at', StageSetting.E_AFTER_START_TIMESLOT, Settings.SETTING_TYPE.E_STRING),
        ('delay', 0, Settings.SETTING_TYPE.E_INT),
        ('delay-start-timer-until-start-timeslot', True, Settings.SETTING_TYPE.E_BOOL),
    )),
]

def get_stage_settings():
    stage_settings = {}
    for stage in stage_settings_config:
        stage_name = stage[0]
        for setting in stage[1]:
            setting_name = '-'.join([stage_name, setting[0]])
            found, value = get_setting(setting_name, 1)
            if found:
                stage_settings[setting_name] = value
            else:
                add_setting(setting_name, setting[1], setting[2], 1)
                stage_settings[setting_name] = setting[1]
    return stage_settings

def set_stage_setting(setting, value):
    return set_setting(setting, value, 1)