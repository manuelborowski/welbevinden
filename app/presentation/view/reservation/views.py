from . import reservation
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus, button_pressed
from app.data import guest as mguest
from app.application import socketio as msocketio, reservation as mreservation
from app.data.models import Guest
from app.presentation.view import update_available_timeslots, false, true, null, prepare_registration_form

import json


@reservation.route('/reservation', methods=['POST', 'GET'])
@login_required
@supervisor_required
def show():
    return base_multiple_items.show(table_configuration)


@reservation.route('/reservation/table_ajax', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration)


@reservation.route('/reservation/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    pass
    if button_pressed('edit'):
        return item_edit()


def item_edit(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        # if chbx_id_list:
        #     id = int(chbx_id_list[0])  # only the first one can be edited
        # reservation = mreservation.get_reservation_by_id(id)
        # config_data = prepare_registration_form(reservation.reservation_code)
        # return render_template('guest/register.html', config_data=config_data,
        #                        registration_endpoint = 'reservation.reservation_save')
    except Exception as e:
        log.error(f'could not edit reservation {request.args}: {e}')
        return redirect(url_for('reservation.show'))

@reservation.route('/reservation_save/<string:form_data>', methods=['POST', 'GET'])
@login_required
@supervisor_required
def reservation_save(form_data):
    try:
        data = json.loads(form_data)
        # if data['cancel-reservation']:
        #     try:
        #         mreservation.delete_registration(data['reservation-code'])
        #     except Exception as e:
        #         flash_plus('Kon de reservatie niet verwijderen', e)
        # else:
        #     try:
        #         ret = mreservation.add_or_update_registration(data, suppress_send_ack_email=True)
        #         if ret.result == ret.Result.E_NO_BOXES_SELECTED:
        #             flash_plus('U hebt geen boxen geselecteerd',)
        #         if ret.result == ret.Result.E_OK:
        #             flash_plus('Reservatie is aangepast')
        #         if ret.result == ret.Result.E_NOT_ENOUGH_BOXES:
        #             flash_plus('Er zijn niet genoeg boxen')
        #     except Exception as e:
        #         flash_plus('Onbekende fout opgetreden', e)
    except Exception as e:
        flash_plus('Onbekende fout opgetreden', e)
    return redirect(url_for('reservation.show'))


def reservation_update_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-reservation', 'data': {'reload-table': True}})


mreservation.subscribe_reservation_changed(reservation_update_cb, None)


def celledit_event_cb(msg, client_sid=None):
    if msg['data']['column'] == 5:
        mreservation.update_reservation('invite_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 7:
        mreservation.update_reservation('ack_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 9:
        mreservation.update_reservation('enabled', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 10:
        mreservation.update_reservation('email_send_retry', msg['data']['id'], msg['data']['value'])
    msocketio.send_to_room({'type': 'celledit-reservation', 'data': {'status': True}}, client_sid)


msocketio.subscribe_on_type('celledit-reservation', celledit_event_cb)


table_configuration = {
    'view': 'reservation',
    'title': 'Reservaties',
    'buttons': [
        # 'delete', 'add', 'edit', 'view'
        'edit'
    ],
    'delete_message': u'Wilt u deze reservatie(s) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'Tijdslot', 'data': 'timeslot', 'order_by': Guest.timeslot, 'orderable': True},
        {'name': 'Email', 'data': 'email', 'order_by': Guest.email, 'orderable': True},
        {'name': 'Naam', 'data': 'full_name', 'order_by': Guest.full_name, 'orderable': True},
        {'name': 'Telefoon', 'data': 'phone', 'order_by': Guest.phone, 'orderable': True},
        {'name': 'Uitndg', 'data': 'invite_email_sent', 'order_by': Guest.invite_email_sent, 'width': '2%', 'celltoggle': 'standard'},
        {'name': 'Uitndg', 'data': 'nbr_invite_sent', 'order_by': Guest.nbr_invite_sent, 'width': '2%'},
        {'name': 'Bevtg', 'data': 'ack_email_sent', 'order_by': Guest.ack_email_sent, 'width': '2%', 'celltoggle': 'standard'},
        {'name': 'Bevtg', 'data': 'nbr_ack_sent', 'order_by': Guest.nbr_ack_sent, 'width': '2%'},
        {'name': 'Actief', 'data': 'enabled', 'order_by': Guest.enabled, 'width': '2%', 'celltoggle': 'standard'},
        {'name': 'Retry', 'data': 'email_send_retry', 'order_by': Guest.email_send_retry, 'orderable': True, 'celledit': 'text'},
    ],
    'filter': [],
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mguest.pre_filter,
    'format_data': mguest.format_data,
    'search_data': mguest.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-reservation',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
