from app.data import timeslot_configuration as mtc
from app import log, db
import datetime, sys


def add_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot):
    try:
        tc = mtc.get_first_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot)
        if tc:
            return
        mtc.add_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


add_timeslot_configuration(datetime.datetime(2021, 5, 1, 9, 0), 15, 12, 8)
add_timeslot_configuration(datetime.datetime(2021, 5, 1, 12, 0), 15, 4, 5)
add_timeslot_configuration(datetime.datetime(2021, 5, 1, 13, 0), 15, 16, 8)
add_timeslot_configuration(datetime.datetime(2021, 5, 5, 13, 0), 15, 16, 5)
