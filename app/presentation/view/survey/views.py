from . import survey
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.application import socketio as msocketio, settings as msettings, cardpresso as mcardpresso, formio as mformio
from app.presentation.view.formio_popups import update_password, database_integrity_check
from app.application.util import deepcopy
import sys, json, re
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

def iterate_form_cb(component, opaque):
    if component and "key" in component:
        if component["key"] == "container-ouders" and opaque["survey-for"] == "leerlingen":
            del(component["components"])
        elif component["key"] == "container-leerlingen" and opaque["survey-for"] == "ouders":
            del(component["components"])
        elif component["key"] == "select-klas":
            if opaque["klassen"] == []:
                component["hidden"] = True
            else:
                data = {"values": [{"label": k, "value": k} for k in opaque["klassen"]]}
                component["data"] = data
        elif component["key"] == "container-select-leerling" and not opaque["toon-leerlingenlijst"]:
            component["hidden"] = True
        elif component["key"] == "container-leerling-data" and not opaque["toon-leerlingenlijst"]:
            del(component["conditional"])
        elif component["key"] == "ss-selecteer-basisschool" and opaque["type"] == "basisschool":
            component["hidden"] = True
        elif component["key"] == "bs-welke-secundaire-school" and opaque["type"] == "secundaireschool":
            component["hidden"] = True
        elif component["key"] == "ss-selecteer-basisschool":
                data = [{"label": k, "value": k} for k in opaque["basisscholen"]]
                component["data"]["values"].extend(data)


@survey.route('/survey/start/<string:type>/<string:code>', methods=['GET'])
def start(type, code):
    try:
        school_infos = msettings.get_configuration_setting("school-profile")
        basisscholen = []
        school_info = None
        for naam, info in school_infos.items():
            if code == info["schoolcode"]:
                school_info = info
                school_info["naam"] = naam
            if info["type"] == "basisschool":
                basisscholen.append(naam)
        if not school_info or type not in ["ouders", "leerlingen"]: return "Sorry, er is een fout opgetreden"
        survey_template = deepcopy(msettings.get_configuration_setting("survey-formio-template"))
        school_info["survey-for"] = type
        school_info["basisscholen"] = basisscholen
        mformio.iterate_components_cb(survey_template, iterate_form_cb, school_info)
        default = {
            "school-type-code": f'{info["schoolcode"]}-{type}'
        }
        data = {'template': survey_template, "default": default}
        return render_template('/survey/start_survey.html', data=data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


@survey.route('/survey/done', methods=['POST'])
def done():
    try:
        data = json.loads(request.data)
        school_infos = msettings.get_configuration_setting("school-profile")
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


