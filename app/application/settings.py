from app.data import settings as msettings, school as mschool, student as mstudent, utils as mutils
from app import log
import sys


def get_default_values():
    try:
        default_settings = msettings.get_configuration_settings(convert_to_string=True)
        school_infos = mschool.get_school_info_for_current_user()
        schooljaar = mutils.get_current_schoolyear()
        for name, info in school_infos.items():
            count = mstudent.get_students({"schoolcode": info["schoolcode"], "schooljaar": schooljaar}, count=True)
            default_settings[f"{name}-upload-leerlingen-lijst-indicator"] = f"{count} studenten in schooljaar {schooljaar}"
        return default_settings
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def get_configuration_settings(convert_to_string=False):
    return msettings.get_configuration_settings(convert_to_string=convert_to_string)


def get_configuration_setting(setting):
    return msettings.get_configuration_setting(setting)


def set_configuration_setting(setting, value):
    msettings.set_configuration_setting(setting, value)


def set_setting_topic(settings):
    try:
        for _, user_level_container in settings.items():
            for key, container in user_level_container.items():
                if 'submit' in container and container['submit']:
                    if key in update_container_cbs:
                        update_container_cbs[key]['cb'](key, container, update_container_cbs[key]['opaque'])
                    else:
                        for k, v in container.items():
                            if k in update_setting_cbs:
                                if update_setting_cbs[k]['cb'](k, v, update_setting_cbs[k]['opaque']):
                                    msettings.set_configuration_setting(k, v)
                            else:
                                msettings.set_configuration_setting(k, v)
                    for k, v in button_clicked_cbs.items():
                        if k in container and container[k]:
                            v['cb'](k, v['opaque'])
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


# a container is a number of settings to be processed
update_container_cbs = {}


def subscribe_update_container(topic, cb, opaque):
    update_container_cbs[topic] = {'cb': cb, 'opaque': opaque}


# a setting is a single setting
update_setting_cbs = {}


def subscribe_update_setting(topic, cb, opaque):
    update_setting_cbs[topic] = {'cb': cb, 'opaque': opaque}


button_clicked_cbs = {}


def subscribe_button_clicked(topic, cb, opaque):
    button_clicked_cbs[topic] = {'cb': cb, 'opaque': opaque}
