from app.application.util import datetime_to_dutch_datetime_string, formiodate_to_datetime, datetime_to_formiodate
from app.data import utils as mutils, guest as mguest, settings as msettings, timeslot_configuration as mtc
from app import log
import datetime, json, sys


def prepare_reservation(code=None):
    try:
        guest = mguest.get_first_guest(code=code)
        if not guest:
            return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)
        default_values = guest.flat()
        if guest.timeslot:
            default_values['update-reservation'] = 'true'
        ret = {'default_values': default_values,
               'template': json.loads(msettings.get_configuration_setting('register-template')),
               'available_timeslots': get_available_timeslots(guest.timeslot)
               }
        return RegisterResult(RegisterResult.Result.E_OK, ret)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return RegisterResult(RegisterResult.Result.E_NOK)


def delete_reservation(code):
    try:
        guest = mguest.get_first_guest(code=code)
        mguest.update_timeslot(guest, None)
        return RegisterResult(result=RegisterResult.Result.E_OK)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return RegisterResult(result=RegisterResult.Result.E_NOK)


def add_or_update_reservation(data, suppress_send_ack_email=False):
    try:
        code = data['reservation-code']
        guest = mguest.get_first_guest(code=code)
        timeslot = formiodate_to_datetime(data['radio-timeslot'])
        if timeslot != guest.timeslot and not check_requested_timeslot(timeslot):
            return RegisterResult(RegisterResult.Result.E_TIMESLOT_FULL, guest.flat())
        guest = mguest.update_guest(guest, data['first-name'], data['last-name'], data['phone'], timeslot)
        if guest and not suppress_send_ack_email:
            guest.set_email_send_retry(0)
            guest.set_ack_email_sent(False)
        return RegisterResult(RegisterResult.Result.E_OK, guest.flat())
    except Exception as e:
        mutils.raise_error(f'could not add registration {data["name-school"]}', e)
    return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)


def update_registration_email_sent_by_id(id, value):
    try:
        pass
        # return mreservation.update_registration_email_sent_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update registration email-sent {id}, {value}', e)
    return None


def update_registration_email_enable_by_id(id, value):
    try:
        pass
        # return mreservation.update_registration_email_enable_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update registration enable email {id}, {value}', e)
    return None


def subscribe_registration_ack_email_sent(cb, opaque):
    pass
    # return mreservation.subscribe_registration_ack_email_sent(cb, opaque)


def get_available_timeslots(default_date=None):
    try:
        timeslots = []
        timeslot_configs = mtc.get_timeslot_configurations()
        for timeslot_config in timeslot_configs:
            date = timeslot_config.date
            for i in range(timeslot_config.nbr_of_timeslots):
                nbr_guests = mguest.get_guest_count(date)
                available = timeslot_config.items_per_timeslot - nbr_guests
                default_flag = default_date and date == default_date
                if default_flag:
                    available += 1
                timeslots.append({
                    'label':  f"({available}) {datetime_to_dutch_datetime_string(date)}",
                    'value': datetime_to_formiodate(date),
                    'available': available,
                    'default': default_flag
                })
                date += datetime.timedelta(minutes=timeslot_config.length)
        return timeslots
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return []


def check_requested_timeslot(date):
    try:
        timeslots = []
        tcs = mtc.get_timeslot_configurations()
        for tc in tcs:
            start_date = tc.date
            end_date = tc.date + datetime.timedelta(minutes=(tc.nbr_of_timeslots * tc.length))
            if start_date <= date <= end_date:
                guest_count = mguest.get_guest_count(date)
                return guest_count < tc.items_per_timeslot
        return False
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return False


class RegisterResult:
    def __init__(self, result, ret={}):
        self.result = result
        self.ret = ret

    class Result:
        E_OK = 'ok'
        E_NOK = 'nok'
        E_REGISTER_OK = 'guest-ok'
        E_COULD_NOT_REGISTER = 'could-not-register'
        E_TIMESLOT_FULL = 'timeslot-full'

    result = Result.E_OK
    ret = {}


def get_reservation_by_id(id):
    pass
    # return mreservation.get_registration_by_id(id)


def delete_meeting(id=None, list=None):
    pass
    # return mmeeting.delete_meeting(id, list)


def update_meeting_code_by_id(id, value):
    try:
        pass
        # return mmeeting.update_meeting_code_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting code {id}, {value}', e)
    return None


def update_meeting_email_sent_by_id(id, value):
    try:
        pass
        # return mmeeting.update_meeting_email_sent_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting email-sent {id}, {value}', e)
    return None


def update_meeting_email_enable_by_id(id, value):
    try:
        pass
        # return mmeeting.update_meeting_email_enable_by_id(id, value)
    except Exception as e:
        mutils.raise_error(f'could not update meeting enable email {id}, {value}', e)
    return None


def subscribe_meeting_ack_email_sent(cb, opaque):
    pass
    # return mmeeting.subscribe_meeting_ack_email_sent(cb, opaque)

# add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
# add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
# add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
# add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
# add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)
