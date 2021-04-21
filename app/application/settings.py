from app.data import settings as msettings


def get_configuration_settings():
    return msettings.get_configuration_settings()


def set_configuration_setting(setting, value):
    msettings.set_configuration_setting(setting, value)
