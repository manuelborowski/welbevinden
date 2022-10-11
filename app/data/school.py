from flask_login import current_user

from app.data import settings as msettings
from app import log
import sys

def get_school_info_for_school(school):
    try:
        school_settings = msettings.get_configuration_setting('school-profile')
        for name, settings in school_settings.items():
            if name == school:
                return settings
        return None
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


# get the school, or scholen the current user belongs to
# if username is of form school-level (e.g. 3neten-sec) and the school exists, then return a list with a single school (3neten)
# if username is not of form school-level (e.g. admin) return a list of all schools
def get_school_info_for_current_user():
    try:
        out = []
        scholen = get_school_from_username()
        school_settings = msettings.get_configuration_setting('school-profile')
        for name, settings in school_settings.items():
            if name in scholen:
                out.append({
                    "name": name,
                    "settings": settings
                })
        return out
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_school_from_username():
    username = current_user.username
    scholen = msettings.get_configuration_setting('school-profile')
    if '-' in username:
        school = username.split('-')[0]
        if school in scholen:
            return [school]
        else:
            return []
    else:
        return [k for k,v in scholen.items()]