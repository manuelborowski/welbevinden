from . import opq
from app import log
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import datatables
from app.application import socketio as msocketio, survey as msurvey, school as mschool
import sys, json, html
import app.data.survey
import app.application.survey
from app.data.datatables import DatatableConfig

@opq.route('/opq/', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    ret = datatables.show(opq_table_config)
    # print('opq.show', datetime.datetime.now() - start)
    return ret


@opq.route('/opq/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    ret = datatables.ajax(opq_table_config)
    # print('opq.table_ajax', datetime.datetime.now() - start)
    return ret


@opq.route('/opq/table_action', methods=['GET', 'POST'])
@opq.route('/opq/table_action/<string:action>', methods=['GET', 'POST'])
@opq.route('/opq/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    return redirect(url_for('opq.show'))


def get_filters():
    filters = []
    klassen = []
    scholen = mschool.get_school_info_for_current_user()
    if scholen:
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
        filters.append({'type': 'select', 'name': 'schoolkey', 'label': 'School', 'choices': school_choices, 'default': school_default,})

    schooljaren = msurvey.get_schooljaren()
    if schooljaren:
        schooljaar_choices = [[s, s] for s in schooljaren]
        schooljaar_default = schooljaar_choices[0][0]
        filters.append({'type': 'select', 'name': 'schooljaar', 'label': 'Schooljaar', 'choices': schooljaar_choices, 'default': schooljaar_default,})
    periodes = msurvey.get_periodes()
    if periodes:
        periode_choices = [[s, s] for s in periodes]
        periode_default = periode_choices[0][0]
        filters.append({'type': 'select', 'name': 'period', 'label': 'Periode', 'choices': periode_choices, 'default': periode_default, })
    targetgroups = msurvey.get_targetgroups()
    if targetgroups:
        targetgroup_choices = [[s, s] for s in targetgroups]
        targetgroup_default = targetgroup_choices[0][0]
        filters.append({'type': 'select', 'name': 'targetgroup', 'label': 'Doelgroep', 'choices': targetgroup_choices, 'default': targetgroup_default,})
    if klassen:
        filters.append({'type': 'select', 'name': 'klas', 'label': 'Klas', 'choices': klas_choices, 'default': klas_default,})
    return filters


class OpqConfig(DatatableConfig):
    def pre_sql_query(self):
        return app.data.survey.pre_sql_query_opq()

    def pre_sql_filter(self, q, filter):
        return app.data.survey.pre_sql_filter_opq(q, filter)

    def format_data(self, l, total_count, filtered_count):
        return app.application.survey.format_data_opq(l, total_count, filtered_count)

    def post_sql_search(self, l, search, count):
        return app.application.survey.post_sql_search_opq(l, search, count)

    def show_filter_elements(self):
        return get_filters()

    enable_column_visible_selector = False
    enable_persistent_filter_settings = False
    default_order = [1, "asc"]


opq_table_config = OpqConfig("opq", "Overzicht per vraag")
