from app.application.util import datetime_to_dutch_datetime_string, create_random_string
from app.application import guest as maguest, formio as mformio
from app.data import utils as mutils, guest as mguest, settings as msettings, timeslot_configuration as mtc
from app.data.models import Guest
from app import log
import datetime, json, sys
from json.decoder import JSONDecodeError

class MessageType:
    E_GENERIC = 'message-generic'
    E_ERROR = 'message-error'


def prepare_registration():
    try:
        return {'template': json.loads(msettings.get_configuration_setting('register-template'))}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_registration_form(code):
    try:
        guest = mguest.get_first_guest({"code": code})
        template = json.loads(msettings.get_configuration_setting('register-template'))
        template = mformio.prepare_for_edit(template)
        return {'template': template,
                'defaults': guest.flat()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_add_registration_form():
    try:
        template = json.loads(msettings.get_configuration_setting('register-template'))
        template = mformio.prepare_for_edit(template)
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def get_confirmation_document(code):
    try:
        template = json.loads(msettings.get_configuration_setting('web-response-template'))
        guest = mguest.get_first_guest({'code': code})
        if _check_register_status(guest):
            template = mformio.prepare_sub_component(template, 'register-child-ack-document-ok', guest)
        else:
            template = mformio.prepare_sub_component(template, 'register-child-ack-document-waiting-list', guest)
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(code)
        raise e


# TODO : check if registration fits in register...
def registration_done(code):
    try:
        template = json.loads(msettings.get_configuration_setting('web-response-template'))
        guest = mguest.get_first_guest({'code': code})
        #check the register settings to see if the student is registered or is on the waiting list
        if _check_register_status(guest):
            template = mformio.prepare_sub_component(template, 'register-child-ack-ok', guest)
        else:
            template = mformio.prepare_sub_component(template, 'register-child-ack-waiting-list', guest)
        # send confirmation e-mail
        if msettings.get_configuration_setting('enable-send-register-ack-mail'):
            mguest.update_guest(guest, {"reg_ack_nbr_tx": 0, "reg_ack_email_tx": False})
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(code)
        raise e


def timeslot_registration_done(code):
    try:
        template = json.loads(msettings.get_configuration_setting('timeslot-web-response-template'))
        guest = mguest.get_first_guest({'code': code})
        template = mformio.prepare_sub_component(template, 'timeslot-register-ack-ok', guest)
        # send confirmation e-mail
        if msettings.get_configuration_setting('timeslot-enable-send-register-ack-mail'):
            mguest.update_guest(guest, {"tsl_ack_nbr_tx": 0, "tsl_ack_email_tx": False})
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(code)
        raise e


def check_register_status(code):
    try:
        guest = mguest.get_first_guest({'code': code})
        #check the register settings to see if the student is registered or is on the waiting list
        return {'status': True, 'data': _check_register_status(guest)}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(code)
        return {"status": False, "data": f'generic error {e}'}


def registration_add(data, suppress_send_ack_email=False):
    try:
        data_selection = {  #duplicates are detetected when email AND childs name are already in database
            'email': data['email'],
            'child_first_name': data['child_first_name'],
            'child_last_name': data['child_last_name']
        }
        duplicate_guest = mguest.get_first_guest(data_selection)
        if duplicate_guest:
            return {"status": False, "data": f"Fout, de student {duplicate_guest.child_first_name} {duplicate_guest.child_last_name} en mailadres {duplicate_guest.email}\n is reeds geregistreerd."}
        misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
        extra_fields = [c['veldnaam'] for c in misc_config]
        extra_field = {f: '' for f in extra_fields}
        data['misc_field'] = json.dumps(extra_field)
        data['code'] = create_random_string()
        data['date_of_birth'] = mformio.formiodate_to_date(data['date_of_birth_dutch'])
        data['register_timestamp'] = datetime.datetime.now()
        guest = mguest.add_guest(data)
        _update_register_status(guest)
        notify_registration_changed()
        log.info(f"New registration: {guest.email}, {guest.child_last_name} {guest.child_first_name} {guest.register_timestamp}")
        return {"status": True, "data": guest.code}
    except JSONDecodeError as e:
        return {"status": False, "data": f'error: JSON decoder: {e}'}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def _update_register_status(guest):
    reg_label = guest.field_of_study.split('-')[0]
    register_settings = json.loads(msettings.get_configuration_setting('register-register-settings'))
    max_nbr_regular = register_settings[reg_label]['max-number-regular-registrations']
    max_nbr_indicator = register_settings[reg_label]['max-number-indicator-registrations']
    overflow = register_settings[reg_label]['overflow-indicator-to-regular']
    if overflow:
        guests = mguest.get_guests(data={'enabled': True}, special={'register_timestamp_<=': guest.register_timestamp,
                                            'field_of_study_like': guest.field_of_study}, order_by='register_timestamp')
        for g in guests:
            if g.indicator:
                max_nbr_indicator -= 1
                if max_nbr_indicator < 0:
                    max_nbr_regular -= 1
            else:
                max_nbr_regular -= 1
        if guest.indicator:
            status = guest.Status.E_REGISTERED if max_nbr_indicator >= 0 or max_nbr_regular >= 0 else guest.Status.E_WAITINGLIST
        else:
            status = guest.Status.E_REGISTERED if max_nbr_regular >= 0 else guest.Status.E_WAITINGLIST
    else:
        if guest.indicator:
            nbr_indicator_guests = mguest.get_guest_register_count(reg_label, guest.register_timestamp, True)
            status = guest.Status.E_REGISTERED if nbr_indicator_guests <= max_nbr_indicator else guest.Status.E_WAITINGLIST
        else:
            nbr_regular_guests = mguest.get_guest_register_count(reg_label, guest.register_timestamp, False)
            status = guest.Status.E_REGISTERED if nbr_regular_guests <= max_nbr_regular else guest.Status.E_WAITINGLIST
    mguest.update_guest(guest, {'status': status})
    return status != guest.Status.E_WAITINGLIST


# return True if the guest is not in the waiting-list
def _check_register_status(guest):
    return guest.status != guest.Status.E_WAITINGLIST


def prepare_timeslot_registration(code=None):
    try:
        guest = mguest.get_first_guest({'code': code})
        if not guest:
            template = json.loads(msettings.get_configuration_setting('timeslot-web-response-template'))
            template = mformio.prepare_sub_component(template, 'timeslot-register-error-wrong-code')
            return {'template': template}
        now = datetime.datetime.now()
        timeslot_registration_open = msettings.get_configuration_setting('open-timeslot-registration-datetime')
        timeslot_registration_open = mformio.formiodate_to_datetime(timeslot_registration_open)
        if now < timeslot_registration_open:
            template = json.loads(msettings.get_configuration_setting('timeslot-web-response-template'))
            template = mformio.prepare_sub_component(template, 'timeslot-registration-not-open',
                     additional_fields={'timeslot_registration_open_dutch': mutils.datetime_to_dutch_datetime_string(timeslot_registration_open)})
            return {'template': template}
        available_timeslots = get_available_timeslots(guest.timeslot)
        template = json.loads(msettings.get_configuration_setting('timeslot-register-template'))
        mformio.update_available_timeslots(available_timeslots, template, 'radio-timeslot')
        data = {
            'template': template,
            'defaults': guest.flat()}
        return data
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def prepare_message(type = MessageType.E_GENERIC, message = None):
    template = json.loads(msettings.get_configuration_setting('web-response-template'))
    template = mformio.prepare_sub_component(template, type, None, {'message': message})
    return RegisterResult(RegisterResult.Result.E_OK, {'template': template})


def delete_registration(code):
    try:
        guest = mguest.get_first_guest(code=code)
        mguest.update_timeslot(guest, None)
        guest.set(Guest.SUBSCRIBE.E_CANCEL_EMAIL_TX, False)
        notify_registration_changed()
        log.info(f'registration cancelled: {guest.email}')
        return RegisterResult(result=RegisterResult.Result.E_OK)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return RegisterResult(result=RegisterResult.Result.E_NOK)


def registration_update(code, data):
    try:
        guest = mguest.get_first_guest({"code": code})
        if 'date_of_birth_dutch' in data:
            data['date_of_birth'] = mformio.formiodate_to_date(data['date_of_birth_dutch'])
        if 'status' in data:    #reset the email tx counter when the status is changed
            data['reg_ack_nbr_tx'] = 0
        if 'status' in data and data['status'] == Guest.Status.E_UNREGISTERED:
            data['unregister_timestamp'] = datetime.datetime.now()
            data['enabled'] = False
        if 'radio-timeslot' in data:
            timeslot = mformio.formiodate_to_datetime(data['radio-timeslot'])
            if timeslot != guest.timeslot and not check_requested_timeslot(timeslot):
                return {"status": False, "data": "Opgepast, het gekozen tijdslot is zojuist volzet geraakt.\nGelieve een nieuw tijdslot te kiezen."}
            data['timeslot'] = timeslot
        mguest.update_guest(guest, data)
        return {"status": True, "data": guest.code}
    except JSONDecodeError as e:
        return {"status": False, "data": f'error: JSON decoder: {e}'}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def notify_registration_changed(value=None):
    for cb in registration_changed_cb:
        cb[0](value, cb[1])


registration_changed_cb = []

def registration_subscribe_changed(cb, opaque):
    try:
        registration_changed_cb.append((cb, opaque))
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def guest_property_change_cb(type, value, opaque):
    notify_registration_changed(value)

Guest.subscribe(Guest.SUBSCRIBE.E_ALL, guest_property_change_cb, None)

def get_registration_counters():
    reserved_guests = mguest.get_guests(enabled=True, timeslot_is_not_none=True)
    open_guests = mguest.get_guests(enabled=True, timeslot_is_none=True)
    child_names = [g.child_first_name for g in reserved_guests]
    filtered_open_guest = [g for g in open_guests if g.child_first_name not in child_names]
    nbr_open = len(filtered_open_guest)
    nbr_reserved = len(reserved_guests)
    nbr_total = nbr_open + nbr_reserved
    return nbr_total, nbr_open, nbr_reserved


def display_register_counters():
    register_settings = json.loads(msettings.get_configuration_setting('register-register-settings'))
    display = []
    for reg, data in register_settings.items():
        nbr_regular_guests = mguest.get_guest_register_count(reg, indicator=False)
        nbr_indicator_guests = mguest.get_guest_register_count(reg, indicator=True)
        max_nbr_regular = data['max-number-regular-registrations']
        max_nbr_indicator = data['max-number-indicator-registrations']
        overflow = " (overloop)" if data['overflow-indicator-to-regular'] else " (geen overloop)"
        display.append(f"{reg}{overflow}, regulier: {nbr_regular_guests}/{max_nbr_regular}, indicator: {nbr_indicator_guests}/{max_nbr_indicator}")
    return display


def get_available_timeslots(default_date=None, ignore_availability=False):
    try:
        timeslots = []
        id = 0
        timeslot_configs = mtc.get_timeslot_configurations()
        for timeslot_config in timeslot_configs:
            date = timeslot_config.date
            for i in range(timeslot_config.nbr_of_timeslots):
                nbr_guests = mguest.get_guest_count({'enabled': True, 'timeslot': date})
                available = timeslot_config.items_per_timeslot - nbr_guests
                default_flag = default_date and date == default_date
                if default_flag:
                    available += 1
                if available > 0 or ignore_availability:
                    timeslots.append({
                        'label':  f"({available}) {datetime_to_dutch_datetime_string(date)}",
                        'value': mformio.datetime_to_formio_datetime(date),
                        'available': available,
                        'default': default_flag,
                        'maximum': timeslot_config.items_per_timeslot,
                        'id': id
                    })
                date += datetime.timedelta(minutes=timeslot_config.length)
                id += 1
        return timeslots
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return []


def datatable_get_timeslots():
    out = []
    timeslots = get_available_timeslots(ignore_availability=True)
    for timeslot in timeslots:
        em = {
            'row_action': timeslot["id"],
            'id': timeslot["id"],
            'DT_RowId': timeslot["id"],
            'timeslot': timeslot['label'],
            'nbr_total': timeslot['maximum'],
            'nbr_open': timeslot['available'],
            'nbr_reserved': timeslot['maximum'] - timeslot['available']
        }
        out.append(em)
    return out


# return true if the current number of guests is less than the maximum
def check_requested_timeslot(date):
    try:
        tcs = mtc.get_timeslot_configurations()
        for tc in tcs:
            start_date = tc.date
            end_date = tc.date + datetime.timedelta(minutes=(tc.nbr_of_timeslots * tc.length))
            if start_date <= date <= end_date:
                guest_count = mguest.get_guest_count({'timeslot': date, 'enabled': True})
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

