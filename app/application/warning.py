from app import log
from app.data import warning as mwarning
import datetime, sys


def new_warning(message):
    try:
        timestamp = datetime.datetime.now()
        mwarning.add_warning({'message': message, 'timestamp': timestamp})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_warning(id, data):
    try:
        warning = mwarning.get_first_warning({'id': id})
        warning = mwarning.update_warning(warning, data)
        if warning:
            inform_warning_updated('*')
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


warning_updated_cbs = []
def subscribe_updated(cb, opaque):
    try:
        warning_updated_cbs.append((cb, opaque))
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')

def inform_warning_updated(type, value=None, opaque=None):
    for cb in warning_updated_cbs:
        cb[0](value, cb[1])


# new_warning('test1')
# new_warning('test2')
# new_warning('Een extra lange test om te zien of het wel klopt wat er allemaal gezegd is geweest.  Ik denk het wel, maar toch')