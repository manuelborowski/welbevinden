from . import timeslot  
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus, button_pressed
from app.data import timeslot_configuration as mtc
from app.application import registration as mregistration
from app.data.models import TimeslotConfiguration

import json


@timeslot.route('/timeslot', methods=['POST', 'GET'])
@login_required
@supervisor_required
def show():
    return base_multiple_items.show(table_configuration)


@timeslot.route('/timeslot/table_ajax', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration)


@timeslot.route('/timeslot/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    return redirect(url_for('timeslot.show'))


table_configuration = {
    'view': 'timeslot',
    'title': 'Tijdsloten',
    'buttons': [],
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '1%', 'visible': 'never'},
        {'name': 'Tijdslot', 'data': 'timeslot', 'width': '12%', 'visible': 'yes'},
        {'name': 'Totaal', 'data': 'nbr_total', 'width': '1%', 'visible': 'yes'},
        {'name': 'Open', 'data': 'nbr_open', 'width': '1%', 'visible': 'yes'},
        {'name': 'Gereserveerd', 'data': 'nbr_reserved', 'width': '1%', 'visible': 'yes'},
    ],
    'width': "50%",
    'item': {},
    'href': [],
    # 'pre_filter': mtc.pre_filter,
    'format_data': mregistration.datatable_get_timeslots,
    # 'search_data': mtc.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-timeslot',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
