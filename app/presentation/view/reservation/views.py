from . import reservation
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus, button_pressed
from app.data import guest as mguest
from app.application import socketio as msocketio, reservation as mreservation
from app.data.models import Guest

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
    if button_pressed('edit'):
        return item_edit()
    if button_pressed('add'):
        return item_add()
    if button_pressed('delete'):
        return item_delete()
    return redirect(url_for('reservation.show'))


def item_delete(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        ids = [int(i) for i in chbx_id_list]
        mguest.delete_guest(ids)
    except Exception as e:
        log.error(f'could not delete guest {request.args}: {e}')
    return redirect(url_for('reservation.show'))


def item_edit(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        if chbx_id_list:
            id = int(chbx_id_list[0])  # only the first one can be edited
        guest = mguest.get_first_guest(id=id)
        return redirect(url_for('guest.register', code=guest.code))
    except Exception as e:
        log.error(f'could not edit reservation {request.args}: {e}')
    return redirect(url_for('reservation.show'))


def item_add(done=False, id=-1):
    try:
        return redirect(url_for('guest.register', code='new'))
    except Exception as e:
        log.error(f'could not add reservation {request.args}: {e}')
    return redirect(url_for('reservation.show'))


@reservation.route('/reservation_save/<string:form_data>', methods=['POST', 'GET'])
@login_required
@supervisor_required
def reservation_save(form_data):
    try:
        data = json.loads(form_data)
        if 'cancel-reservation' in data and data['cancel-reservation']:
            try:
                mreservation.delete_reservation(data['reservation-code'])
                flash_plus('Reservatie is verwijderd')
            except Exception as e:
                flash_plus('Kon de reservatie niet verwijderen', e)
        else:
            try:
                ret = mreservation.add_or_update_reservation(data)
                if ret.result == ret.Result.E_OK:
                    flash_plus('Reservatie is aangepast')
                if ret.result == ret.Result.E_TIMESLOT_FULL:
                    flash_plus('Op dit tijdslot zijn er geen plaatsen meer beschikbaar')
            except Exception as e:
                flash_plus('Onbekende fout opgetreden', e)
    except Exception as e:
        flash_plus('Onbekende fout opgetreden', e)
    return redirect(url_for('reservation.show'))


def reservation_update_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-reservation', 'data': {'reload-table': True}})


mreservation.subscribe_reservation_changed(reservation_update_cb, None)


def celledit_event_cb(msg, client_sid=None):
    if msg['data']['column'] == 6:
        mreservation.update_reservation('note', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 7:
        mreservation.update_reservation('invite_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 9:
        mreservation.update_reservation('ack_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 11:
        mreservation.update_reservation('enabled', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 12:
        mreservation.update_reservation('email_send_retry', msg['data']['id'], msg['data']['value'])
    msocketio.send_to_room({'type': 'celledit-reservation', 'data': {'status': True}}, client_sid)


msocketio.subscribe_on_type('celledit-reservation', celledit_event_cb)


def get_filters():
    return [
        {
            'type': 'select',
            'name': 'timeslot',
            'label': 'Reservatie',
            'choices': [
                ['default', 'Alles'],
                ['yes', 'Gemaakt'],
                ['no', 'Open'],
            ],
            'default': 'default',
        },
    ]


def get_show_info():
    nbr_total, nbr_open, nbr_reserved = mreservation.get_reservation_counters()
    return [
        f'Totaal: {nbr_total}',
        f'Open: {nbr_open}',
        f'Gereserveerd: {nbr_reserved}',
    ]


table_configuration = {
    'view': 'reservation',
    'title': 'Gasten',
    'buttons': ['edit', 'add', 'delete'],
    'delete_message': 'Opgelet!!<br>Bent u zeker om deze gast(en) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '1%'},
        {'name': 'Tijdslot', 'data': 'timeslot', 'order_by': Guest.timeslot, 'orderable': True, 'width': '10%'},
        {'name': 'Email', 'data': 'email', 'order_by': Guest.email, 'orderable': True, 'width': '12%'},
        {'name': 'Naam', 'data': 'full_name', 'order_by': Guest.full_name, 'orderable': True, 'width': '12%'},
        {'name': 'Kind', 'data': 'child_name', 'order_by': Guest.child_name, 'orderable': True, 'width': '12%'},
        {'name': 'Telefoon', 'data': 'phone', 'order_by': Guest.phone, 'orderable': True, 'width': '8%'},
        {'name': 'Notitie', 'data': 'note', 'order_by': Guest.note, 'orderable': True, 'width': '25%', 'celledit': 'text'},
        {'name': 'U', 'data': 'invite_email_sent', 'order_by': Guest.invite_email_sent, 'width': '1%',
         'celltoggle': 'standard'},
        {'name': 'U', 'data': 'nbr_invite_sent', 'order_by': Guest.nbr_invite_sent, 'width': '1%'},
        {'name': 'B', 'data': 'ack_email_sent', 'order_by': Guest.ack_email_sent, 'width': '1%',
         'celltoggle': 'standard'},
        {'name': 'B', 'data': 'nbr_ack_sent', 'order_by': Guest.nbr_ack_sent, 'width': '1%'},
        {'name': 'A', 'data': 'enabled', 'order_by': Guest.enabled, 'width': '1%', 'celltoggle': 'standard'},
        {'name': 'R', 'data': 'email_send_retry', 'order_by': Guest.email_send_retry, 'orderable': True,
         'celledit': 'text', 'width': '1%'},
    ],
    'get_filters': get_filters,
    'get_show_info': get_show_info,
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mguest.pre_filter,
    'format_data': mguest.format_data,
    'filter_data': mguest.filter_data,
    'search_data': mguest.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-reservation',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
