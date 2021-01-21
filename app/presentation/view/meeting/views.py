from . import meeting
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.data import reservation as mdreservation, meeting as mmeeting
from app.application import reservation as mreservation, settings as msettings, socketio as msocketio
from app.data.models import SchoolReservation, AvailablePeriod, TeamsMeeting
from app.presentation.layout.utils import flash_plus, button_pressed
from app.presentation.view import update_available_periods, false, true, null, prepare_registration_form

import json


@meeting.route('/meeting', methods=['POST', 'GET'])
@login_required
@supervisor_required
def show():
    return base_multiple_items.show(table_configuration)


@meeting.route('/meeting/table_ajax', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration)


@meeting.route('/meeting/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    pass
    # if button_pressed('edit'):
    #     return item_edit()


def update_meeting_cb(msg, client_sid=None):
    if msg['data']['column'] == 6: # code column
        mreservation.update_meeting_code_by_id(msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 7: # mail sent column
        mreservation.update_meeting_email_sent_by_id(msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 8: # enable send mail column
        mreservation.update_meeting_email_enable_by_id(msg['data']['id'], msg['data']['value'])
    msocketio.send_to_room({'type': 'celledit-meeting', 'data': {'status': True}}, client_sid)

msocketio.subscribe_on_type('celledit-meeting', update_meeting_cb)


def ack_email_sent_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-meeting', 'data': {'reload-table': True}})


mreservation.subscribe_ack_email_sent(ack_email_sent_cb, None)


table_configuration = {
    'view': 'meeting',
    'title': 'Team Meetings',
    'buttons': [
        # 'delete', 'add', 'edit', 'view'
        'edit'
    ],
    'delete_message': u'Wilt u deze meeting(s) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'School', 'data': 'reservation.name-school', 'order_by': SchoolReservation.name_school, 'orderable': True},
        {'name': 'Klas', 'data': 'classgroup', 'order_by': TeamsMeeting.classgroup, 'orderable': True},
        {'name': 'E-mail', 'data': 'meeting-email', 'order_by': TeamsMeeting.email, 'orderable': True},
        {'name': 'Moment', 'data': 'meeting-date', 'order_by': TeamsMeeting.date, 'orderable': True},
        {'name': 'Meeting URL', 'data': 'html_url', 'order_by': TeamsMeeting.teams_meeting_code, 'orderable': True},
        {'name': 'Code', 'data': 'code', 'order_by': TeamsMeeting.teams_meeting_code, 'orderable': True, 'celledit' : 'text'},
        {'name': 'Zend e-mail', 'data': 'email_sent', 'order_by': TeamsMeeting.ack_email_sent, 'orderable': True,'celltoggle' : 'standard'},
        {'name': 'Actief', 'data': 'enabled', 'order_by': TeamsMeeting.enabled, 'orderable': True,'celltoggle' : 'standard'},
    ],
    'filter': [],
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mmeeting.pre_filter,
    'format_data': mmeeting.format_data,
    'search_data': mmeeting.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-meeting',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
