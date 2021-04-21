from app.data import timeslot_configuration
from app import log, db
import datetime


timeslot_configuration.add_timeslot_configuration(datetime.datetime(2021, 5, 1, 9, 0), 15, 32, 8)
timeslot_configuration.add_timeslot_configuration(datetime.datetime(2021, 5, 5, 13, 0), 15, 16, 5)
