from . import survey
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.application import socketio as msocketio, settings as msettings, survey as msurvey, school as mschool
from app.presentation.view.formio_popups import update_password, database_integrity_check
from app.application.util import deepcopy
import sys, json, re, html
import app.data.survey
import app.application.survey


@survey.route('/survey/survey', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration)
    # print('survey.show', datetime.datetime.now() - start)
    return ret


@survey.route('/survey/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.ajax(table_configuration)
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


def get_filters():
    klassen = []
    scholen = mschool.get_school_info_for_current_user()
    school_choices = [[k, s["label"]] for k, s in scholen.items()]
    if len(scholen) == 1:
        school_default = school_choices[0][0]
        klassen = msurvey.get_klassen({"schoolkey": school_default})
        if klassen:
            klas_choices = [['all', 'Alle']] + [[s, s] for s in klassen]
            klas_default = klas_choices[0][0]
    else:
        school_choices = [['all', 'Alle']] + school_choices
        school_default = "all"
    schooljaren = msurvey.get_schooljaren()
    schooljaar_choices = [[s, s] for s in schooljaren]
    schooljaar_default = schooljaar_choices[0][0]
    periodes = msurvey.get_periodes()
    periode_choices = [[s, s] for s in periodes]
    periode_default = periode_choices[0][0]
    targetgroups = msurvey.get_targetgroups()
    targetgroup_choices = [[s, s] for s in targetgroups]
    targetgroup_default = targetgroup_choices[0][0]

    filters = [
        {
            'type': 'select',
            'name': 'school',
            'label': 'School',
            'choices': school_choices,
            'default': school_default,
        },
        {
            'type': 'select',
            'name': 'schooljaar',
            'label': 'Schooljaar',
            'choices': schooljaar_choices,
            'default': schooljaar_default,
        },
        {
            'type': 'select',
            'name': 'periode',
            'label': 'Periode',
            'choices': periode_choices,
            'default': periode_default,
        },
        {
            'type': 'select',
            'name': 'targetgroup',
            'label': 'Doelgroep',
            'choices': targetgroup_choices,
            'default': targetgroup_default,
        },
    ]
    if klassen:
        filters.append({
            'type': 'select',
            'name': 'klas',
            'label': 'Klas',
            'choices': klas_choices,
            'default': klas_default,
        })
    return filters


table_configuration = {
    'view': 'survey',
    'title': 'Resultaten van de bevraging',
    'buttons': [],
    'href': [],
    'get_filters': get_filters,
    'pre_filter': app.data.survey.pre_filter,
    'format_data': app.application.survey.format_data,
    'filter_data': app.data.survey.filter_data,
    'search_data': app.data.survey.search_data,
    'default_order': (2, 'asc'),
    'socketio_endpoint': 'celledit-survey',
    "suppress_column_visible_selector": True,
    "suppress_persistent_filter_settings": True
}


@survey.route('/survey/start/<string:period>/<string:targetgroup>/<string:schoolcode>', methods=['GET'])
def start(period, targetgroup, schoolcode):
    try:
        data = msurvey.prepare_survey(period, targetgroup, schoolcode)
        return render_template('/survey/survey_formio.html', data=data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return html.escape(str(e))

@survey.route('/survey/save', methods=['POST'])
def save():
    try:
        data = json.loads(request.data)
        data = msurvey.save_survey(data)
        return json.dumps({"status": True, "data": data})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})


@survey.route('/survey/done', methods=['GET'])
def done():
    try:
        # data = json.loads(request.data)
        data = msurvey.survey_done(request.values)
        return render_template('/survey/survey_formio.html', data=data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})


