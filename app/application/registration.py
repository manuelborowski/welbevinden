from app.application import formio as mformio, util as mutil
from app.data import utils as mdutils, guest as mguest, settings as msettings, timeslot_configuration as mtc
from app.data.guest import get_guests, get_guest_register_last_timestamp
from app.data.models import Guest
from app import log
import datetime, json, sys
from json.decoder import JSONDecodeError

class MessageType:
    E_GENERIC = 'message-generic'
    E_ERROR = 'message-error'


def prepare_registration():
    try:
        return {'template': mutil.get_json_template('student-register-template')}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_registration_form(code):
    try:
        guest = mguest.get_first_guest({"code": code})
        template = mutil.get_json_template('student-register-template')
        template = mformio.prepare_for_edit(template)
        return {'template': template,
                'defaults': guest.flat()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_add_registration_form():
    try:
        template = mutil.get_json_template('student-register-template')
        template = mformio.prepare_for_edit(template)
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def get_confirmation_document(code):
    try:
        template = mutil.get_json_template('student-web-response-template')
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


def registration_done(code):
    try:
        template = mutil.get_json_template('student-web-response-template')
        guest = mguest.get_first_guest({'code': code})
        #check the register settings to see if the student is registered or is on the waiting list
        if _check_register_status(guest):
            template = mformio.prepare_sub_component(template, 'register-child-ack-ok', guest)
        else:
            template = mformio.prepare_sub_component(template, 'register-child-ack-waiting-list', guest)
        # send confirmation e-mail
        if msettings.get_configuration_setting('student-register-arm-send-ack-mail'):
            mguest.update_guest(guest, {"reg_ack_nbr_tx": 0, "reg_ack_email_tx": False})
        return {'template': template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(code)
        raise e


def timeslot_registration_done(code):
    try:
        template = mutil.get_json_template('timeslot-web-response-template')
        guest = mguest.get_first_guest({'code': code})
        template = mformio.prepare_sub_component(template, 'timeslot-register-ack-ok', guest)
        # send confirmation e-mail
        if msettings.get_configuration_setting('timeslot-register-arm-send-ack-mail'):
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


def registration_add(data):
    try:
        data_selection = {  #duplicates are detetected when email AND childs name are already in database
            'email': data['email'],
            'child_first_name': data['child_first_name'],
            'child_last_name': data['child_last_name']
        }
        duplicate_guest = mguest.get_first_guest(data_selection)
        if duplicate_guest:
            return {"status": False, "data": f"Fout, de student {duplicate_guest.child_first_name} {duplicate_guest.child_last_name} en mailadres {duplicate_guest.email}\n is reeds geregistreerd."}
        misc_config = mutil.get_json_template('import-misc-fields')
        extra_fields = [c['veldnaam'] for c in misc_config]
        extra_field = {f: '' for f in extra_fields}
        data['misc_field'] = json.dumps(extra_field)
        data['code'] = mutil.create_random_string()
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
    register_settings = mutil.get_json_template('student-register-settings')
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
            template = mutil.get_json_template('timeslot-web-response-template')
            template = mformio.prepare_sub_component(template, 'timeslot-register-error-wrong-code')
            return {'template': template}
        now = datetime.datetime.now()
        timeslot_registration_open = msettings.get_configuration_setting('timeslot-open-registration-at')
        timeslot_registration_open = mformio.formiodate_to_datetime(timeslot_registration_open)
        if now < timeslot_registration_open:
            template = mutil.get_json_template('timeslot-web-response-template')
            template = mformio.prepare_sub_component(template, 'timeslot-registration-not-open',
                                                     additional_fields={'timeslot_registration_open_dutch': mdutils.datetime_to_dutch_datetime_string(timeslot_registration_open)})
            return {'template': template}
        available_timeslots = get_available_timeslots(guest.timeslot)
        template = mutil.get_json_template('timeslot-register-template')
        mformio.update_available_timeslots(available_timeslots, template, 'radio-timeslot')
        data = {'template': template,'defaults': guest.flat()}
        return data
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


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


def display_register_counters():
    register_settings = mutil.get_json_template('student-register-settings')
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
                        'label':  f"({available}) {mutil.datetime_to_dutch_datetime_string(date)}",
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


def format_data(db_list):
    register_settings = mutil.get_json_template('student-register-settings')
    register_info = {}
    for r, d in register_settings.items():
        max_nbr_indicator = d['max-number-indicator-registrations']
        max_nbr_regular = d['max-number-regular-registrations']
        info = {'regular_timestamp': None, 'indicator_timestamp': None, 'regular_counter': 1, 'indicator_counter': 1}
        if d['overflow-indicator-to-regular']:
            guests = get_guests(data={'enabled': True}, special={'field_of_study_like': r}, order_by='register_timestamp')
            for g in guests:
                if g.indicator:
                    if max_nbr_indicator > 0:
                        max_nbr_indicator -= 1
                        info['indicator_timestamp'] = g.register_timestamp
                    elif max_nbr_regular > 0:
                        max_nbr_regular -= 1
                        info['indicator_timestamp'] = g.register_timestamp
                elif max_nbr_regular > 0:
                    max_nbr_regular -= 1
                    info['regular_timestamp'] = g.register_timestamp
        else:
            regular_guest = get_guest_register_last_timestamp(r, max_nbr_regular, indicator=False)
            indicator_guest = get_guest_register_last_timestamp(r, max_nbr_indicator, indicator=True)
            if regular_guest:
                info['regular_timestamp'] = regular_guest.register_timestamp
            if indicator_guest:
                info['indicator_timestamp'] = indicator_guest.register_timestamp
        register_info[r] = info
    out = []
    for i in db_list:
        em = i.flat()
        em.update({
            'row_action': i.code,
            'id': i.id,
            'DT_RowId': i.code
        })
        em['sequence_counter'] = ""
        if i.enabled:
            info = register_info[em['register']]
            timestamp = info['indicator_timestamp' if i.indicator else 'regular_timestamp']
            if timestamp and i.register_timestamp > timestamp:
                em['overwrite_cell_color'].append(['register_timestamp_dutch', 'yellow'])
            else:
                em['overwrite_cell_color'].append(['register_timestamp_dutch', 'greenyellow'])
                if i.indicator:
                    em['sequence_counter'] = info['indicator_counter']
                    info['indicator_counter'] += 1
                    em['overwrite_cell_color'].append(['sequence_counter', 'aqua'])
                else:
                    em['sequence_counter'] = info['regular_counter']
                    info['regular_counter'] += 1
                    em['overwrite_cell_color'].append(['sequence_counter', 'turquoise'])
            if i.status == Guest.Status.E_REGISTERED:
                em['overwrite_cell_color'].append(['status', 'greenyellow'])
            else:
                em['overwrite_cell_color'].append(['status', 'yellow'])
        else:
            em['overwrite_cell_color'].append(['enabled', 'red'])
        if i.reg_ack_nbr_tx == 0:
            em['overwrite_cell_color'].append(['reg_ack_nbr_tx', 'orange'])
            em['overwrite_cell_color'].append(['reg_ack_email_tx', 'orange'])
        if i.tsl_ack_nbr_tx == 0:
            em['overwrite_cell_color'].append(['tsl_ack_nbr_tx', 'orange'])
            em['overwrite_cell_color'].append(['tsl_ack_email_tx', 'orange'])

        out.append(em)
    return out