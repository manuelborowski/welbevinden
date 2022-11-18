import datetime, sys
from app.data.settings import get_configuration_setting

from sqlalchemy import desc

from app import flask_app, log, data, db
from app.data import models as mmodels


def datetime_to_dutch_datetime_string(date, include_seconds=False):
    return mmodels.datetime_to_dutch_datetime_string(date, include_seconds=include_seconds)


def raise_error(message, details=None):
    error = Exception(f'm({message}), d({details}), td({type(details).__name__})')
    raise error


# standardized way to make a key from strings: sort alphabetically and concatenate
def make_key(item_list):
    return make_list(item_list, seperator=',')

def extend_key(item1, item2=None):
    if isinstance(item1, list):
        return ','.join(item1)
    return ','.join([item1, item2])


# standardized way to concatenate strings: sort alphabetically and concatenate; seperated by comma
def make_list(item_list, seperator=', '):
    return seperator.join(sorted(item_list))


def get_current_schoolyear():
	try:
		test_schooljaar = get_configuration_setting("test-schooljaar")
		if test_schooljaar != "":
			return f"TEST-{test_schooljaar}"
		now = datetime.datetime.now()
		if now.month <= 8:
			current_schoolyear = f'{now.year - 1}-{now.year}'
		else:
			current_schoolyear = f'{now.year}-{now.year + 1}'
		return current_schoolyear
	except Exception as e:
		log.error(f'{sys._getframe().f_code.co_name}: {e}')
	return False


def get_test_bevragingen():
	test_schooljaar = get_configuration_setting("test-schooljaar")
	return test_schooljaar != ""
