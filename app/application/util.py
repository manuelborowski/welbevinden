import random, string, sys
from app.data import utils as mutils
from app import log


def datetime_to_dutch_datetime_string(date):
    return mutils.datetime_to_dutch_datetime_string(date)


def create_random_string(len=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def process_api_options(options):
    try:
        fields = options['fields'].split(',') if 'fields' in options else []
        filters = {}
        if 'filters' in options:
            for filter in options['filters'].split(','):
                k_v = filter.split('=')
                filters[k_v[0]] = k_v[1]
        return fields, filters
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
