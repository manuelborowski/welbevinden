from app.application.util import datetime_to_dutch_datetime_string, formiodate_to_datetime, datetime_to_formiodate, create_random_string
from app.application import formio
from app.application import guest as maguest
from app.data import utils as mutils, guest as mguest, settings as msettings, timeslot_configuration as mtc
from app.data.models import Guest
from app import log
import datetime, json, sys


def prepare_registration():
    data = {
        'template': json.loads(msettings.get_configuration_setting('register-template'))
    }
    return RegisterResult(RegisterResult.Result.E_OK, data)


def get_confirmation_document(code):
    data_selection = {
        'code': code,
    }
    guest = mguest.get_first_guest(data_selection)
    ack_template = json.loads(msettings.get_configuration_setting('web-response-template'))
    ack_template = formio.prepare_component(ack_template, 'register-child-ack-document-ok', guest)
    return RegisterResult(RegisterResult.Result.E_OK, {'guest_info': guest.flat(),
                                                       'template': ack_template})


# TODO : check if registration fits in register...
def add_registration(data, suppress_send_ack_email=False):
    try:
        ack_template = json.loads(msettings.get_configuration_setting('web-response-template'))

        data_selection = {  #duplicates are detetected when email and childs name are already found in database
            'email': data['email'],
            'child_first_name': data['child_first_name'],
            'child_last_name': data['child_last_name']
        }
        # duplicate_guest = mguest.get_first_guest(data_selection)
        # if duplicate_guest:
        #     ack_template = formio.prepare_component(ack_template, 'register-child-ack-already-registered', duplicate_guest)
        #     return RegisterResult(RegisterResult.Result.E_DUPLICATE_REGISTRATION, ack_template)

        misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
        extra_fields = [c['veldnaam'] for c in misc_config]
        extra_field = {f: '' for f in extra_fields}
        data['misc_field'] = json.dumps(extra_field)
        data['code'] = create_random_string()
        guest = mguest.add_guest(data)
        # if guest and not suppress_send_ack_email:
        #     guest.set(Guest.SUBSCRIBE.EMAIL_TOT_NBR_TX, 0)
        #     guest.set(Guest.SUBSCRIBE.REG_ACK_EMAIL_TX, False)
        ack_template = formio.prepare_component(ack_template, 'register-child-ack-ok', guest)
        # timeslot = datetime_to_dutch_datetime_string(guest.timeslot)
        # register_ack_template = register_ack_template.replace('{{TAG_TIMESLOT}}', timeslot)
        return RegisterResult(RegisterResult.Result.E_OK, {'guest_info': guest.flat(),
                                                           'template': ack_template})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
    return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)


def prepare_timeslot_registration(code=None):
    try:
        if 'new' == code:
            empty_values = {
            'phone': '',
            'email': '',
            'full_name': '',
            'child_name': '',
            'registration-code': 'new',
            }
            ret = {'default_values': empty_values,
                   'template': json.loads(msettings.get_configuration_setting('register-template')),
                   'available_timeslots': get_available_timeslots(),
                   'mode': 'new'
                   }
            if not ret['available_timeslots']:
                return RegisterResult(RegisterResult.Result.E_NO_TIMESLOT, None)
            return RegisterResult(RegisterResult.Result.E_OK, ret)
        else:
            guest = mguest.get_first_guest(code=code)
            if not guest:
                return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)
            default_values = guest.flat()
            if guest.timeslot:
                default_values['update-registration'] = 'true'
            ret = {'default_values': default_values,
                   'template': json.loads(msettings.get_configuration_setting('register-template')),
                   'available_timeslots': get_available_timeslots(guest.timeslot),
                   'mode': 'update'
                   }
            return RegisterResult(RegisterResult.Result.E_OK, ret)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return RegisterResult(RegisterResult.Result.E_NOK)


def delete_registration(code):
    try:
        guest = mguest.get_first_guest(code=code)
        mguest.update_timeslot(guest, None)
        guest.set(Guest.SUBSCRIBE.CANCEL_EMAIL_TX, False)
        log.info(f'registration cancelled: {guest.email}')
        return RegisterResult(result=RegisterResult.Result.E_OK)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return RegisterResult(result=RegisterResult.Result.E_NOK)


def add_or_update_registration(data, suppress_send_ack_email=False):
    try:
        code = data['registration-code']
        timeslot = formiodate_to_datetime(data['radio-timeslot'])
        if 'new' == code:
            if data['email'] == '' or data['child_name'] == '':
                return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)
            if not check_requested_timeslot(timeslot):
                ret = {'registration-code': 'new'}
                return RegisterResult(RegisterResult.Result.E_TIMESLOT_FULL, ret)
            misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
            extra_fields = [c['veldnaam'] for c in misc_config]
            extra_field = {f: '' for f in extra_fields}
            data['misc_field'] = extra_field
            guest = maguest.add_guest(data)
        else:
            guest = mguest.get_first_guest({'code': code})
            if timeslot != guest.timeslot and not check_requested_timeslot(timeslot):
                return RegisterResult(RegisterResult.Result.E_TIMESLOT_FULL, guest.flat())
            guest = mguest.update_guest(guest, data)
        if guest and not suppress_send_ack_email:
            guest.set(Guest.SUBSCRIBE.EMAIL_TOT_NBR_TX, 0)
            guest.set(Guest.SUBSCRIBE.REG_ACK_EMAIL_TX, False)
        register_ack_template = msettings.get_configuration_setting('register-ack-template')
        timeslot = datetime_to_dutch_datetime_string(guest.timeslot)
        register_ack_template = register_ack_template.replace('{{TAG_TIMESLOT}}', timeslot)
        return RegisterResult(RegisterResult.Result.E_OK, register_ack_template)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
    return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)


def update_registration(property, id, value):
    try:
        guest = mguest.get_first_guest(id=id)
        if 'note' == property:
            mguest.update_guest(guest, note=value)
        if 'invite_email_sent' == property:
            guest.set(Guest.SUBSCRIBE.INVITE_EMAIL_TX, value)
        elif 'ack_email_sent' == property:
            guest.set(Guest.SUBSCRIBE.REG_ACK_EMAIL_TX, value)
        elif 'cancel_email_sent' == property:
            guest.set(Guest.SUBSCRIBE.CANCEL_EMAIL_TX, value)
        elif 'enabled' == property:
            guest.set(Guest.SUBSCRIBE.ENABLED, value)
        elif 'email_send_retry' == property:
            guest.set(Guest.SUBSCRIBE.EMAIL_TOT_NBR_TX, value)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


registration_changed_cb = []


def subscribe_registration_changed(cb, opaque):
    try:
        registration_changed_cb.append((cb, opaque))
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def guest_property_change_cb(type, value, opaque):
    for cb in registration_changed_cb:
        cb[0](value, cb[1])


Guest.subscribe(Guest.SUBSCRIBE.ALL, guest_property_change_cb, None)


def get_registration_counters():
    reserved_guests = mguest.get_guests(enabled=True, timeslot_is_not_none=True)
    open_guests = mguest.get_guests(enabled=True, timeslot_is_none=True)
    child_names = [g.child_first_name for g in reserved_guests]
    filtered_open_guest = [g for g in open_guests if g.child_first_name not in child_names]
    nbr_open = len(filtered_open_guest)
    nbr_reserved = len(reserved_guests)
    nbr_total = nbr_open + nbr_reserved
    return nbr_total, nbr_open, nbr_reserved


def get_available_timeslots(default_date=None, ignore_availability=False):
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
                if available > 0 or ignore_availability:
                    timeslots.append({
                        'label':  f"({available}) {datetime_to_dutch_datetime_string(date)}",
                        'value': datetime_to_formiodate(date),
                        'available': available,
                        'default': default_flag,
                        'maximum': timeslot_config.items_per_timeslot,
                    })
                date += datetime.timedelta(minutes=timeslot_config.length)
        return timeslots
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return []


def datatable_get_timeslots():
    out = []
    timeslots = get_available_timeslots(ignore_availability=True)
    for timeslot in timeslots:
        em = {
            'row_action': "0",
            'id': 0,
            'DT_RowId': 0,
            'timeslot': timeslot['label'],
            'nbr_total': timeslot['maximum'],
            'nbr_open': timeslot['available'],
            'nbr_reserved': timeslot['maximum'] - timeslot['available']
        }
        out.append(em)
    return out



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
    def __init__(self, result, data={}):
        self.result = result
        self.data = data

    class Result:
        E_OK = 'ok'
        E_NOK = 'nok'
        E_REGISTER_OK = 'guest-ok'
        E_COULD_NOT_REGISTER = 'could-not-register'
        E_TIMESLOT_FULL = 'timeslot-full'
        E_NO_TIMESLOT = 'no-timeslot'
        E_DUPLICATE_REGISTRATION = 'duplicate-registration'

    result = Result.E_OK
    data = {}

