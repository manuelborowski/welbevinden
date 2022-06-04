from . import cardpresso
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings
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
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    if action == 'delete':
        return item_delete(ids)
    return redirect(url_for('cardpresso.show'))


@cardpresso.route('/cardpresso/get_form', methods=['POST', 'GET'])
@login_required
def get_form():
    try:
        common = {
            'post_data_endpoint': 'api.cardpresso_update',
            'submit_endpoint': 'cardpresso.show',
            'cancel_endpoint': 'cardpresso.show',
            'api_key': flask_app.config['API_KEY']
        }
        if request.values['form'] == 'pdf':
            data = app.application.cardpresso_cardpresso.prepare_edit_form(request.values['extra'], read_only=True, pdf=True)
            data.update(common)
        elif current_user.is_at_least_supervisor:
            if request.values['form'] == 'edit':
                data = app.application.cardpresso_cardpresso.prepare_edit_form(request.values['extra'])
                data.update(common)
            elif request.values['form'] == 'add':
                data = app.application.cardpresso_cardpresso.prepare_add_form()
                data.update(common)
                data['post_data_endpoint'] ='api.cardpresso_add'
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
        app.application.cardpresso_cardpresso.delete_cardpressos(ids)
    except Exception as e:
        log.error(f'could not delete cardpresso {request.args}: {e}')
    return redirect(url_for('cardpresso.show'))


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('cardpresso.show'))
        else:
            id = ids[0]
        return render_template('formio.html', data={"form": "edit",
                                                           "get_form_endpoint": "cardpresso.get_form",
                                                           "extra": id,
                                                           "buttons": ["save", "cancel"]})
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('cardpresso.show'))


@supervisor_required
def item_add():
    try:
        return render_template('formio.html', data={"form": "add",
                                                           "get_form_endpoint": "cardpresso.get_form",
                                                           "buttons": ["save", "cancel", "clear"]})
    except Exception as e:
        log.error(f'Could not add cardpresso {e}')
        flash_plus(f'Kan cardpresso niet toevoegen: {e}')
    return redirect(url_for('cardpresso.show'))


# # propagate changes in (some) properties to the table
# def registration_update_cb(value, opaque):
#     msocketio.broadcast_message({'type': 'celledit-cardpresso', 'data': {'reload-table': True}})
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
    msocketio.send_to_room({'type': 'celledit-cardpresso', 'data': {'status': True}}, client_sid)

msocketio.subscribe_on_type('celledit-cardpresso', celledit_event_cb)


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
    'view': 'cardpresso',
    'title': 'Studenten-badge',
    'buttons': ['edit', 'add', 'delete'],
    'delete_message': 'Opgelet!!<br>'
                      'Bent u zeker om deze student(en) te verwijderen?<br>'
                      'Eens verwijderd kunnen ze niet meer worden terug gehaald.<br>',
    'get_filters': get_filters,
    'item': {
        'edit': {'title': 'Wijzig een cardpresso', 'buttons': ['save', 'cancel']},
        'add': {'title': 'Voeg een cardpresso toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': app.data.cardpresso.pre_filter,
    'format_data': app.application.cardpresso.format_data,
    'filter_data': app.data.cardpresso.filter_data,
    'search_data': app.data.cardpresso.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-cardpresso',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
