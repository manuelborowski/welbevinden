import random, string, json, re
from app.data import utils as mutils, settings as msettings


def datetime_to_dutch_datetime_string(date):
    return mutils.datetime_to_dutch_datetime_string(date)


def create_random_string(len=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def get_json_template(key):
    template_string = msettings.get_configuration_setting(key)
    if template_string == '':
        raise Exception(f'Empty template: {key}')
    try:
        settings = json.loads(template_string)
    except json.JSONDecodeError as e:
        raise Exception(f'Template has invalid JSON syntax: {key} {e}')
    return settings


def set_json_template(key, data):
    try:
        template_string = json.dumps(data)
        template_string = re.sub('},', '},\n', template_string)
        return msettings.set_configuration_setting(key, template_string)
    except json.JSONDecodeError as e:
        raise Exception(f'Template has invalid JSON syntax: {key}, {data}, {e}')
