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
# @supervisor_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    if action == 'delete':
        return item_delete(ids)
    return redirect(url_for('student.show'))


@student.route('/student/get_form', methods=['POST', 'GET'])
@login_required
def get_form():
    try:
        common = {
            'post_data_endpoint': 'api.student_update',
            'submit_endpoint': 'student.show',
            'cancel_endpoint': 'student.show',
            'api_key': flask_app.config['API_KEY']
        }
        if current_user.is_at_least_supervisor:
            if request.values['form'] == 'edit':
                data = app.application.student.prepare_edit_form(request.values['extra'])
                data.update(common)
            elif request.values['form'] == 'add':
                data = app.application.student.prepare_add_form()
                data.update(common)
                data['post_data_endpoint'] ='api.student_add'
            else:
                return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
        else:
            return {"status": False, "data": f"U hebt geen toegang tot deze url"}
        return {"status": True, "data": data}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}


@supervisor_required
def item_delete(ids=None):
    try:
        if ids == None:
            ids = request.form.getlist('chbx')
        app.application.student_student.delete_students(ids)
    except Exception as e:
        log.error(f'could not delete student {request.args}: {e}')
    return redirect(url_for('student.show'))


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('student.show'))
        else:
            id = ids[0]
        return render_template('formio.html', data={"form": "edit",
                                                           "get_form_endpoint": "student.get_form",
                                                           "extra": id,
                                                           "buttons": ["cancel"]})
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('student.show'))


@supervisor_required
def item_add():
    try:
        return render_template('formio.html', data={"form": "add",
                                                           "get_form_endpoint": "student.get_form",
                                                           "buttons": ["save", "cancel", "clear"]})
    except Exception as e:
        log.error(f'Could not add student {e}')
        flash_plus(f'Kan student niet toevoegen: {e}')
    return redirect(url_for('student.show'))


@student.route('/student/right_click/', methods=['POST', 'GET'])
@login_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "new-badge":
                    ret = mcardpresso.add_new_badges(data['item_ids'])
                    return {"message": ret['data']}
                if data['item'] == "view":
                    return {"redirect": f"/student/table_action/edit/[{data['item_id']}]"}

    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}
    return {"status": False, "data": "iets is fout gelopen"}



# # propagate changes in (some) properties to the table
# def registration_update_cb(value, opaque):
#     msocketio.broadcast_message({'type': 'celledit-student', 'data': {'reload-table': True}})
#
# mregistration.registration_subscribe_changed(registration_update_cb, None)

# some columns can be edit inplace in the table.
def celledit_event_cb(msg, client_sid=None):
    try:
        nbr = msg['data']['column']
        column_template = table_configuration['template'][nbr]
        if 'celltoggle' in column_template or 'celledit' in column_template:
            mregistration.registration_update(msg['data']['id'], {column_template['data']: msg['data']['value']})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    msocketio.send_to_room({'type': 'celledit-student', 'data': {'status': True}}, client_sid)

msocketio.subscribe_on_type('celledit-student', celledit_event_cb)


def get_misc_fields(extra_fields, form):
    misc_field = {}
    for field in extra_fields:
        if field in form:
            misc_field[field] = form[field]
    return misc_field


def get_filters():
    filters = []
    return filters


table_configuration = {
    'view': 'student',
    'title': 'Studenten',
    'buttons': [],
    'get_filters': get_filters,
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

