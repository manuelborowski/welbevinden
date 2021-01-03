from app.data import settings as msettings


def get_stage_settings():
    return msettings.get_stage_settings()


def set_stage_setting(setting, value):
    return msettings.set_stage_setting(setting, value)


class StageSetting(msettings.StageSetting):
    pass
