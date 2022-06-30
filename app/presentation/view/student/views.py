from . import student
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings, cardpresso as mcardpresso
import sys, json
import app.data
import app.application.student


@student.route('/student/student', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration, template='student/student.html')
    # print('student.show', datetime.datetime.now() - start)
    return ret


@student.route('/student/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('student.table_ajax', datetime.datetime.now() - start)
    return ret


@student.route('/student/table_action', methods=['GET', 'POST'])
@student.route('/student/table_action/<string:action>', methods=['GET', 'POST'])
@student.route('/student/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'view':
        return item_view(ids)
    return redirect(url_for('student.show'))


item_common = {'post_data_endpoint': 'api.student_update', 'submit_endpoint': 'student.show', 'cancel_endpoint': 'student.show', 'api_key': flask_app.config['API_KEY']}
#
#
# @student.route('/student/get_form', methods=['POST', 'GET'])
# @login_required
# def get_form():
#     try:
#         common = {
#             'post_data_endpoint': 'api.student_update',
#             'submit_endpoint': 'student.show',
#             'cancel_endpoint': 'student.show',
#             'api_key': flask_app.config['API_KEY']
#         }
#         if request.values['form'] == 'view':
#             data = app.application.student.prepare_view_form(request.values['extra'])
#             data.update(common)
#             data.update({'title': f"{data['defaults']['naam']} {data['defaults']['voornaam']}"})
#         else:
#             return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
#         return {"status": True, "data": data}
#     except Exception as e:
#         log.error(f"Error in get_form: {e}")
#         return {"status": False, "data": f"get_form: {e}"}
#
#
def item_view(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('student.show'))
        else:
            id = ids[0]
            data = app.application.student.prepare_view_form(id)
            data.update(item_common)
            data.update({'title': f"{data['defaults']['naam']} {data['defaults']['voornaam']}"})
            return render_template('formio.html', data=data)
        # return render_template('formio.html', data={"form": "view",
        #                                                    "get_form_endpoint": "student.get_form",
        #                                                    "extra": id,
        #                                                    "buttons": ["cancel"]})
    except Exception as e:
        log.error(f'Could not view student {e}')
    return redirect(url_for('student.show'))


@student.route('/student/right_click/', methods=['POST', 'GET'])
@login_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "new-badge":
                    ret = mcardpresso.add_badges(data['item_ids'])
                    return {"message": ret['data']}
                if data['item'] == "view":
                    max_ids = msettings.get_configuration_setting('student-max-students-to-view-with-one-click')
                    ids = data['item_ids'][:max_ids]
                    return {"redirect": {"url": f"/student/table_action/view", "ids": ids, "new_tab": True}}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"message": f"get_form: {e}"}
    return {"message": "iets is fout gelopen"}


def get_misc_fields(extra_fields, form):
    misc_field = {}
    for field in extra_fields:
        if field in form:
            misc_field[field] = form[field]
    return misc_field


def get_filters():
    return [
        {
            'type': 'select',
            'name': 'photo-not-found',
            'label': 'Foto\'s',
            'choices': [
                ['default', 'Alles'],
                ['not-found', 'Geen foto'],
            ],
            'default': 'default',
        },
    ]


def get_info():
    return [
        f'Niet gevonden foto\'s: {app.application.student.get_nbr_photo_not_found()}'
    ]

table_configuration = {
    'view': 'student',
    'title': 'Studenten',
    'buttons': [],
    'get_filters': get_filters,
    'get_show_info': get_info,
    'href': [],
    'pre_filter': app.data.student.pre_filter,
    'format_data': app.application.student.format_data,
    'filter_data': app.data.student.filter_data,
    'search_data': app.data.student.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-student',
    'right_click': {
        'endpoint': 'student.right_click',
        'menu': [
            {'label': 'Nieuwe badge', 'item': 'new-badge', 'iconscout': 'credit-card'},
            {'label': 'Details', 'item': 'view', 'iconscout': 'eye'},
            {'label': 'Vsk nummers', 'item': 'new-vsk-numbers', 'iconscout': 'abacus'},
        ]
    }
}

