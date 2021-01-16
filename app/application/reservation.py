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


def get_period_by_id(id):
    return mreservation.get_available_period_by_id(id)


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


class RegisterSaveResult:
    def __init__(self, result, reservation={}):
        self.result = result
        self.reservation = reservation

    class Result:
        E_OK = 'ok'
        E_NO_BOXES_SELECTED = 'no-boxes-selected'
        E_NOT_ENOUGH_BOXES = 'not-enough-boxes'
        E_COULD_NOT_REGISTER = 'could-not-register'

    result = Result.E_OK
    reservation = {}


def add_registration(data):
    try:
        periods = get_available_periods()
        valid_nbr_boxes = False
        for period in periods:
            key = f'select-boxes-{period["id"]}'
            if key in data and (int(data[key]) > 0):
                data['period_id'] = period['id']
                data['nbr_boxes'] = int(data[key])
                valid_nbr_boxes = True
                break
        if not valid_nbr_boxes:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_NO_BOXES_SELECTED)
        period = mreservation.get_available_period_by_id(id=data['period_id'])
        if (period.max_nbr_boxes - period.nbr_boxes_taken) < data['nbr_boxes']:
            return RegisterSaveResult(result=RegisterSaveResult.Result.E_NOT_ENOUGH_BOXES)
        if data['reservation-code'] == '':
            data['reservation-code'] = create_random_string(32)
            reservation=mreservation.add_registration(data)
        else:
            mreservation.update_registration_by_code(data)
        # name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone,
                #                           address, postal_code, city, nbr_students, available_period_id, nbr_boxes,
                #                           meeting_email, date, code)
        # else:
        #     mreservation.update_registration_by_code(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email,
        #                                              phone, address, postal_code, city, nbr_students,
        #                                              available_period_id, nbr_boxes,
        #                                              meeting_email, date, code)
        return RegisterSaveResult(result=RegisterSaveResult.Result.E_OK, reservation=reservation.ret_dict())
    except Exception as e:
        mutils.raise_error(f'could not add registration {data["name-school"]}', e)
    return RegisterSaveResult(result=RegisterSaveResult.Result.E_COULD_NOT_REGISTER)


def prepare_reservation_for_update(code=None):
    try:
        if code == None: return {}
        reservation = mreservation.get_registration_by_code(code)
        flat = reservation.flat()
        mreservation.update_registration(reservation, nbr_boxes=0)
        return flat
    except Exception as e:
        mutils.raise_error(f'could not get reservation by code {code}', e)
    return None


def get_reservation_by_id(id):
    return mreservation.get_registration_by_id(id)


add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)
