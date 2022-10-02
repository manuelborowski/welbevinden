from . import survey
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.application import socketio as msocketio, settings as msettings, cardpresso as mcardpresso
from app.presentation.view.formio_popups import update_password, database_integrity_check
import sys, json
import app.data.survey
import app.application.survey


@survey.route('/survey/survey', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration, template='survey/survey.html')
    # print('survey.show', datetime.datetime.now() - start)
    return ret


@survey.route('/survey/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('survey.table_ajax', datetime.datetime.now() - start)
    return ret


@survey.route('/survey/table_action', methods=['GET', 'POST'])
@survey.route('/survey/table_action/<string:action>', methods=['GET', 'POST'])
@survey.route('/survey/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    return redirect(url_for('survey.show'))


table_configuration = {
    'view': 'survey',
    'title': 'Enquête: lijst van deelnemers',
    'buttons': [],
    'href': [],
    'pre_filter': app.data.survey.pre_filter,
    'format_data': app.application.survey.format_data,
    'filter_data': app.data.survey.filter_data,
    'search_data': app.data.survey.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-survey',
}

