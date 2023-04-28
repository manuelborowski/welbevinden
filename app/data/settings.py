import re
import sys

from flask_login import current_user
from app import log, db
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import MEDIUMTEXT
import json


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'
        E_JSON = 'JSON'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(MEDIUMTEXT)
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer)

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)



# return: found, value
# found: if True, setting was found else not
# value ; if setting was found, returns the value
def get_setting(name, id=-1, convert_to_string=False):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_INT:
            value = int(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_FLOAT:
            value = float(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = True if setting.value == 'True' else False
        elif setting.type == Settings.SETTING_TYPE.E_JSON:
            value = json.dumps(json.loads(setting.value), indent=2) if convert_to_string else json.loads(setting.value)
        else:
            value = setting.value
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return False, ''
    return True, value


def add_setting(name, value, type, id=-1):
    try:
        if type == Settings.SETTING_TYPE.E_JSON:
            value = json.dumps(value)
        setting = Settings(name=name, value=str(value), type=type, user_id=id if id > -1 else current_user.id)
        db.session.add(setting)
        db.session.commit()
        log.info('add: {}'.format(setting.log()))
        return True
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def set_setting(name, value, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting:
            if setting.type == Settings.SETTING_TYPE.E_BOOL:
                value = 'True' if value else 'False'
            elif setting.type == Settings.SETTING_TYPE.E_JSON:
                if type(value) is dict:
                    value = json.dumps(value)
                else:
                    value = json.dumps(json.loads(value))
            setting.value = value
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return False
    return True


default_configuration_settings = {
    'user-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'user-datatables-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'user-login-max-tries': (5, Settings.SETTING_TYPE.E_INT),

    'survey-sept-ouders-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'survey-sept-leerlingen-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'survey-nov-ouders-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'survey-nov-leerlingen-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'survey-done-formio-template': ({}, Settings.SETTING_TYPE.E_JSON),

    'opq-datatables-template': ({}, Settings.SETTING_TYPE.E_JSON),
    'ops-datatables-template': ({}, Settings.SETTING_TYPE.E_JSON),

    'api-keys': ([], Settings.SETTING_TYPE.E_JSON),

    'school-profile': ({}, Settings.SETTING_TYPE.E_JSON),
    'basisscholen-question-whitelist': ({}, Settings.SETTING_TYPE.E_JSON),

    'test-schooljaar': ("", Settings.SETTING_TYPE.E_STRING),
}


def get_configuration_settings(convert_to_string=False):
    configuration_settings = {}
    for k in default_configuration_settings:
        configuration_settings[k] = get_configuration_setting(k, convert_to_string)
    return configuration_settings


def set_configuration_setting(setting, value):
    if None == value:
        value = default_configuration_settings[setting][0]
    ret = set_setting(setting, value, 1)
    if setting in setting_changed_cb:
        for cb in setting_changed_cb[setting]:
            cb[0](value, cb[1])
    return ret


def get_configuration_setting(setting, convert_to_string=False):
    found, value = get_setting(setting, 1, convert_to_string=convert_to_string)
    if found:
        return value
    else:
        default_setting = default_configuration_settings[setting]
        add_setting(setting, default_setting[0], default_setting[1], 1)
        return default_setting[0]


setting_changed_cb = {}
def subscribe_setting_changed(setting, cb, opaque):
    if setting in setting_changed_cb:
        setting_changed_cb[setting].append((cb, opaque))
    else:
        setting_changed_cb[setting] = [(cb, opaque)]
    return True


def set_json_template(key, data):
    try:
        template_string = json.dumps(data)
        template_string = re.sub('},', '},\n', template_string)
        return set_configuration_setting(key, template_string)
    except json.JSONDecodeError as e:
        raise Exception(f'Template has invalid JSON syntax: {key}, {data}, {e}')

# subscribe_setting_changed('generic-view-config-template', lambda x, y: cache_settings(), None)
# subscribe_setting_changed('student-register-settings', lambda x, y: cache_settings(), None)
# subscribe_setting_changed('generic-translations', lambda x, y: cache_settings(), None)

def get_datatables_config(key):
    return get_configuration_setting(f'{key}-datatables-template')


# Read from formio text-area and format a list.
# Lines with # are ignored
def get_list(list_name):
    out = []
    recepients = get_configuration_setting(list_name)
    if recepients != '':
        recepients = recepients.split('\n')
        out = [r.strip() for r in recepients if '#' not in r]
    return out


