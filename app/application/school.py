import sys
from app import log
from app.data import settings as msettings, school as mschool
from app.application.settings import subscribe_update_container


def handle_school_settings(key, container, opaque):
    try:
        school_settings = msettings.get_configuration_setting('school-profile')
        scholen_container = container["container-scholen"]
        for school, settings in scholen_container.items():
            if school_settings[school]["type"] == "secundaireschool":
                if settings["container-secundaire-school"]["klassen"] == '':
                    school_settings[school]["klassen"] = []
                else:
                    klassen = settings["container-secundaire-school"]["klassen"].split(",")
                    school_settings[school]["klassen"] = [k.strip() for k in klassen]
            school_settings[school]["venster-actief"]["ouders-van"] = settings["ouders-van"]
            school_settings[school]["venster-actief"]["ouders-tot"] = settings["ouders-tot"]
            school_settings[school]["venster-actief"]["leerlingen-van"] = settings["leerlingen-van"]
            school_settings[school]["venster-actief"]["leerlingen-tot"] = settings["leerlingen-tot"]
        msettings.set_configuration_setting('school-profile', school_settings)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


subscribe_update_container('module-school-info', handle_school_settings, None)

def get_school_info_for_current_user():
    return mschool.get_school_info_for_current_user()
