from app.data.models import TimeslotConfiguration
from sqlalchemy import not_
from app.data import utils as mutils
from app import log, db
import datetime, random, string, sys


def add_timeslot_configuration_bulk(date, length, nbr_of_timeslots, items_per_timeslot):
    try:
        timeslot_configuration = TimeslotConfiguration(date=date, length=length, nbr_of_timeslots=nbr_of_timeslots, items_per_timeslot=items_per_timeslot)
        db.session.add(timeslot_configuration)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_timeslot_configuration_commit():
    try:
        db.session.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot):
    try:
        add_timeslot_configuration_bulk(date=date, length=length, nbr_of_timeslots=nbr_of_timeslots, items_per_timeslot=items_per_timeslot)
        add_timeslot_configuration_commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_timeslot_configurations(first=False):
    try:
        timeslot_configurations = TimeslotConfiguration.query
        if first:
            timeslot_configuration = timeslot_configurations.first()
            return timeslot_configuration
        timeslot_configurations = timeslot_configurations.all()
        return timeslot_configurations()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_timeslot_configuration():
    try:
        timeslot_configuration = get_timeslot_configurations()
        return timeslot_configuration
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def pre_filter():
    return db.session.query(TimeslotConfiguration)


def search_data(search_string):
    search_constraints = []
    # search_constraints.append(SchoolReservation.name_school.like(search_string))
    # search_constraints.append(SchoolReservation.name_teacher_1.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out


