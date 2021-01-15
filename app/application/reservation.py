from app.data import utils as mutils, reservation as mreservation
from app import db, log
import datetime, random, string


def add_available_period(period, period_length, max_nbr_boxes):
    return mreservation.add_available_period(period, period_length, max_nbr_boxes)


def get_available_periods():
    available_periods = []
    try:
        periods = mreservation.get_available_periods()
        for period in periods:
            nbr_boxes_taken = period.nbr_boxes_taken
            available_periods.append({
                'id': period.id,
                'period': period.period_string(),
                'length': period.length,
                'max_number': period.max_nbr_boxes,
                'current_number': nbr_boxes_taken,
                'boxes_available': period.max_nbr_boxes - nbr_boxes_taken,
            })
        return available_periods
    except Exception as e:
        mutils.raise_error('could not get available periods', e)
    return []


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def add_registration(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone, address, postal_code,
                     city, nbr_students, available_period_id, nbr_boxes, code, meeting_email, meeting_date):
    try:
        try:
            date = datetime.datetime.strptime(meeting_date.split('+')[0], '%Y-%m-%dT%H:%M:%S')
        except:
            date = None
        period = mreservation.get_available_period(id=available_period_id)
        if (period.max_nbr_boxes - period.nbr_boxes_taken) < nbr_boxes:
            return "not-enough-boxes"
        if code == '':
            code = create_random_string(32)
            mreservation.add_registration(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone,
                                          address, postal_code, city, nbr_students, available_period_id, nbr_boxes,
                                          meeting_email, date, code)
        else:
            mreservation.update_registration_by_code(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email,
                                                     phone, address, postal_code, city, nbr_students,
                                                     available_period_id, nbr_boxes,
                                                     meeting_email, date, code)
        return "ok"
    except Exception as e:
        mutils.raise_error(f'could not add registration {name_school}', e)
    return "unknown-error"


def get_default_reservation_values(code=None, flat=False):
    try:
        if code == None: return {}
        reservation = mreservation.get_registration(code=code)
        period_id_key = f'select-boxes-{reservation.reservation_period_id}'
        flat = {
            'name-school': reservation.name_school,
            'name-teacher-1': reservation.name_teacher_1,
            'name-teacher-2': reservation.name_teacher_2,
            'name-teacher-3': reservation.name_teacher_3,
            'email': reservation.email,
            'phone': reservation.phone,
            'address': reservation.address,
            'postal-code': reservation.postal_code,
            'city': reservation.city,
            'number-students': reservation.nbr_students,
            period_id_key: reservation.reservation_nbr_boxes,
            'meeting-email': reservation.meeting_email,
            'meeting-date': reservation.meeting_date_string(),
            'reservation-code': reservation.reservation_code,
        }
        mreservation.set_registration(reservation, nbr_boxes=0)
        return flat
    except Exception as e:
        mutils.raise_error(f'could not get reservation by code {code}', e)
    return None


add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)
