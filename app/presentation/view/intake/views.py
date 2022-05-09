from . import intake
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio
import sys, json
import app.data
import app.application


@intake.route('/intake/intake', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret = base_multiple_items.show(table_configuration)
    # print('intake.show', datetime.datetime.now() - start)
    return ret


@intake.route('/intake/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret =  base_multiple_items.ajax(table_configuration)
    # print('intake.table_ajax', datetime.datetime.now() - start)
    return ret


@intake.route('/intake/table_action', methods=['GET', 'POST'])
@intake.route('/intake/table_action/<string:action>', methods=['GET', 'POST'])
@intake.route('/intake/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
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
    return redirect(url_for('intake.show'))


@intake.route('/intake/get_form', methods=['POST', 'GET'])
@login_required
def get_form():
    try:
        common = {
            'post_data_endpoint': 'api.intake_update',
            'submit_endpoint': 'intake.show',
            'cancel_endpoint': 'intake.show',
            'api_key': flask_app.config['API_KEY']
        }
        if request.values['form'] == 'view':
            data = app.application.student_intake.prepare_edit_form(request.values['extra'], read_only=True)
            data.update(common)
        elif current_user.is_at_least_supervisor:
            if request.values['form'] == 'edit':
                data = app.application.student_intake.prepare_edit_form(request.values['extra'])
                data.update(common)
            elif request.values['form'] == 'add':
                data = app.application.student_intake.prepare_add_form()
                data.update(common)
                data['post_data_endpoint'] ='api.intake_add'
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
        app.application.student_intake.delete_students(ids)
    except Exception as e:
        log.error(f'could not delete intake {request.args}: {e}')
    return redirect(url_for('intake.show'))


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('intake.show'))
        else:
            id = ids[0]
        return render_template('render_formio.html', data={"form": "edit",
                                                           "get_form_endpoint": "intake.get_form",
                                                           "extra": id,
                                                           "buttons": ["save", "cancel"]})
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('intake.show'))


@supervisor_required
def item_add():
    try:
        return render_template('render_formio.html', data={"form": "add",
                                                           "get_form_endpoint": "intake.get_form",
                                                           "buttons": ["save", "cancel", "clear"]})
    except Exception as e:
        log.error(f'Could not add intake {e}')
        flash_plus(f'Kan intake niet toevoegen: {e}')
    return redirect(url_for('intake.show'))


# # propagate changes in (some) properties to the table
# def registration_update_cb(value, opaque):
#     msocketio.broadcast_message({'type': 'celledit-intake', 'data': {'reload-table': True}})
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
    msocketio.send_to_room({'type': 'celledit-intake', 'data': {'status': True}}, client_sid)

msocketio.subscribe_on_type('celledit-intake', celledit_event_cb)


def get_misc_fields(extra_fields, form):
    misc_field = {}
    for field in extra_fields:
        if field in form:
            misc_field[field] = form[field]
    return misc_field


def get_filters():
    filters = []
    return filters


def get_show_gauges():
    return ''


table_configuration = {
    'view': 'intake',
    'title': 'Inschrijven',
    'buttons': ['edit', 'add', 'delete', 'pdf'],
    'delete_message': 'Opgelet!!<br>'
                      'Bent u zeker om deze intake(en) te verwijderen?<br>'
                      'Eens verwijderd kunnen ze niet meer worden terug gehaald.<br>',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'item': {
        'edit': {'title': 'Wijzig een intake', 'buttons': ['save', 'cancel']},
        'add': {'title': 'Voeg een intake toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': app.data.student_intake.pre_filter,
    'format_data': app.application.student_intake.format_data,
    'filter_data': app.data.student_intake.filter_data,
    'search_data': app.data.student_intake.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-intake',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
