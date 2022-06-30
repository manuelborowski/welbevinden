from . import cardpresso
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, cardpresso as mcardpresso
import sys, json
import app.data
import app.application.cardpresso


@cardpresso.route('/cardpresso/cardpresso', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration)
    # print('cardpresso.show', datetime.datetime.now() - start)
    return ret


@cardpresso.route('/cardpresso/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('cardpresso.table_ajax', datetime.datetime.now() - start)
    return ret


@cardpresso.route('/cardpresso/table_action', methods=['GET', 'POST'])
@cardpresso.route('/cardpresso/table_action/<string:action>', methods=['GET', 'POST'])
@cardpresso.route('/cardpresso/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
# @supervisor_required
def table_action(action, ids=None):
    return redirect(url_for('cardpresso.show'))


@cardpresso.route('/cardpresso/right_click/', methods=['POST', 'GET'])
@login_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "delete":
                    mcardpresso.delete_badges(data['item_ids'])
                    return {"message": "studenten (badges) zijn verwijderd"}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}
    return {"status": False, "data": "iets is fout gelopen"}


def get_filters():
    filters = []
    return filters


table_configuration = {
    'view': 'cardpresso',
    'title': 'Studenten-badge',
    'buttons': [],
    'get_filters': get_filters,
    'href': [],
    'pre_filter': app.data.cardpresso.pre_filter,
    'format_data': app.application.cardpresso.format_data,
    'filter_data': app.data.cardpresso.filter_data,
    'search_data': app.data.cardpresso.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-cardpresso',
    'right_click': {
        'endpoint': 'cardpresso.right_click',
        'menu': [
            {'label': 'Verwijder', 'item': 'delete', 'iconscout': 'trash-alt'},
        ]
    }

}
