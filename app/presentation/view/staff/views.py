from . import staff
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings, cardpresso as mcardpresso
import sys, json
import app.data
import app.application.staff


@staff.route('/staff/staff', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration, template='staff/staff.html')
    # print('staff.show', datetime.datetime.now() - start)
    return ret


@staff.route('/staff/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('staff.table_ajax', datetime.datetime.now() - start)
    return ret


@staff.route('/staff/table_action', methods=['GET', 'POST'])
@staff.route('/staff/table_action/<string:action>', methods=['GET', 'POST'])
@staff.route('/staff/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    return redirect(url_for('staff.show'))


@staff.route('/staff/right_click/', methods=['POST', 'GET'])
@login_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"message": f"get_form: {e}"}
    return {"message": "iets is fout gelopen"}


def get_filters():
    return []


def get_info():
    return []

def get_right_click_settings():
    settings = {
        'endpoint': 'staff.right_click',
        'menu': []
    }
    if current_user.is_at_least_supervisor:
        settings['menu'].extend([
            {'label': 'RFID code', 'item': 'check-rfid', 'iconscout': 'wifi'},
        ])
    return settings


table_configuration = {
    'view': 'staff',
    'title': 'Personeelsleden',
    'buttons': [],
    'get_filters': get_filters,
    'get_show_info': get_info,
    'href': [],
    'pre_filter': app.data.staff.pre_filter,
    'format_data': app.application.staff.format_data,
    'filter_data': app.data.staff.filter_data,
    'search_data': app.data.staff.search_data,
    'default_order': (1, 'asc'),
    'get_right_click': get_right_click_settings,
}

