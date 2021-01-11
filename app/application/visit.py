from app.data import settings as msettings
from app.data.models import Visit
import datetime


def get_timeslots():
    first_timeslot_string = msettings.get_configuration_setting('timeslot-first-start')
    timeslot_length = msettings.get_configuration_setting('timeslot-length')
    nbr_of_timeslots = msettings.get_configuration_setting('timeslot-number')
    max_guests_per_timeslot = msettings.get_configuration_setting('timeslot-max-guests')
    first_timeslot = datetime.datetime.strptime(first_timeslot_string, '%Y-%m-%d-%H:%M:%S')
    timeslot_header = []
    for t in range(nbr_of_timeslots):
        delta_minutes = t * timeslot_length
        timeslot_time =  first_timeslot + datetime.timedelta(minutes=delta_minutes)
        timeslot_header.append({
                'time': timeslot_time.strftime('%H:%M'),
             })
    timeslots = {
        'header': timeslot_header,
        'days': [],
    }
    timeslot_day = {
        'day': first_timeslot.strftime('%d/%m/%Y'),
        'slots': [],
    }
    for t in range(nbr_of_timeslots):
        delta_minutes = t * timeslot_length
        timeslot_time =  first_timeslot + datetime.timedelta(minutes=delta_minutes)
        nbr_guests = Visit.query.filter(Visit.timeslot == timeslot_time).count()
        timeslot_day['slots'].append({
                'time': timeslot_time.strftime('%H:%M'),
                'nbr_of_guests': nbr_guests,
                'max_nbr_of_guests': max_guests_per_timeslot,
                'type': 'free' if nbr_guests < max_guests_per_timeslot else 'taken'
             })
    timeslots['days'].append(timeslot_day)
    return timeslots


