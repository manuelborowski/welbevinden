from app.data import settings as msettings


class StageSetting(msettings.StageSetting):
    pass


def get_configuration_settings():
    return msettings.get_configuration_settings()


def set_configuration_setting(setting, value):
    msettings.set_configuration_setting(setting, value)


def get_register_template():
    return msettings.get_configuration_setting('register-template')