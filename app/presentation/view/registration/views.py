from . import registration
from app import log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus, button_pressed
from app.data import guest as mguest
from app.application import socketio as msocketio, registration as mregistration, settings as msettings
from app.data.models import Guest
import json, sys


@registration.route('/registration/registration', methods=['POST', 'GET'])
@login_required
@supervisor_required
def show():
    misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
    misc_fields = [c['veldnaam'] for c in misc_config]
    base_multiple_items.update(table_configuration, misc_fields)
    return base_multiple_items.show(table_configuration)


@registration.route('/registration/table_ajax', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_ajax():
    misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
    misc_fields = [c['veldnaam'] for c in misc_config]
    base_multiple_items.update(table_configuration, misc_fields)
    return base_multiple_items.ajax(table_configuration)


@registration.route('/registration/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    if button_pressed('edit'):
        return item_edit()
    if button_pressed('add'):
        return item_add()
    if button_pressed('delete'):
        return item_delete()
    return redirect(url_for('registration.show'))


@registration.route('/registration/get_form', methods=['POST', 'GET'])
def get_form():
    try:
        if request.values['form'] == 'edit':
            data = mregistration.prepare_edit_registration_form(request.values['extra'])
            data.update({
                'post_data_endpoint': 'api.register_update',
                'submit_endpoint': 'registration.show',
                'cancel_endpoint': 'registration.show'
            })
        elif request.values['form'] == 'add':
            data = mregistration.prepare_add_registration_form()
            data.update({
                'post_data_endpoint': 'api.register_add',
                'submit_endpoint': 'registration.show',
                'cancel_endpoint': 'registration.show'
            })
        else:
            return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
        return {"status": True, "data": data}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}


def item_delete():
    try:
        chbx_code_list = request.form.getlist('chbx')
        mguest.delete_guest(chbx_code_list)
    except Exception as e:
        log.error(f'could not delete guest {request.args}: {e}')
    return redirect(url_for('registration.show'))


def item_edit():
    try:
        chbx_code_list = request.form.getlist('chbx')
        if chbx_code_list:
            code = chbx_code_list[0]  # only the first one can be edited
        if code == '':
            return redirect(url_for('registration.show'))
        return render_template('render_formio.html', data={"form": "edit",
                                                           "get_form_endpoint": "registration.get_form",
                                                            "extra": code})
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('registration.show'))


def item_add():
    try:
        return render_template('render_formio.html', data={"form": "add",
                                                           "get_form_endpoint": "registration.get_form"})
    except Exception as e:
        log.error(f'Could not add guest {e}')
        flash_plus(f'Kan gebruiker niet toevoegen: {e}')
    return redirect(url_for('registration.show'))


# propagate changes in (some) properties to the table
def registration_update_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-registration', 'data': {'reload-table': True}})

mregistration.subscribe_registration_changed(registration_update_cb, None)

# some columns can be edit inplace in the table.
def celledit_event_cb(msg, client_sid=None):
    try:
        nbr = msg['data']['column']
        column_template = table_configuration['template'][nbr]
        if 'celltoggle' in column_template or 'celledit' in column_template:
            mregistration.update_registration(msg['data']['id'], {column_template['data']: msg['data']['value']})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    msocketio.send_to_room({'type': 'celledit-registration', 'data': {'status': True}}, client_sid)

msocketio.subscribe_on_type('celledit-registration', celledit_event_cb)


def get_misc_fields(extra_fields, form):
    misc_field = {}
    for field in extra_fields:
        if field in form:
            misc_field[field] = form[field]
    return misc_field


def get_filters():
    register_settings = json.loads(msettings.get_configuration_setting('register-register-settings'))
    choices = [['default', 'Alles']]
    for reg, data in register_settings.items():
        choices.append([f"{reg}-N", f"{reg}"])
        choices.append([f"{reg}-R", f"{reg}-REGULIER"])
        choices.append([f"{reg}-I", f"{reg}-INDICATOR"])
    return [
        {
            'type': 'select',
            'name': 'register',
            'label': 'Register',
            'choices': choices,
            'default': 'default',
        },
    ]


def get_show_gauges():
    return mregistration.display_register_counters()


table_configuration = {
    'view': 'registration',
    'title': 'Inschrijvingen',
    'buttons': ['edit', 'add', 'delete'],
    'delete_message': 'Opgelet!!<br>'
                      'Bent u zeker om deze reservering(en) te verwijderen?<br>'
                      'Eens verwijderd kunnen ze niet meer worden terug gehaald.<br>',
    'template': [
        {'name': 'row_action', 'data': 'code', 'width': '1%', 'visible': 'never'},
        {'name': 'Tijdstempel', 'data': 'register_timestamp_dutch', 'order_by': Guest.register_timestamp, 'orderable': True, 'width': '8%', 'visible': 'yes'},
        {'name': 'R', 'data': 'register', 'order_by': Guest.field_of_study, 'orderable': True, 'width': '2%', 'visible': 'yes'},
        {'name': 'I', 'data': 'indicator_dutch', 'order_by': Guest.indicator, 'orderable': True, 'width': '1%', 'className': 'dt-center', 'visible': 'yes'},
        {'name': 'Tijdslot', 'data': 'timeslot', 'order_by': Guest.timeslot, 'orderable': True, 'width': '8%', 'visible': 'yes'},
        {'name': 'Email', 'data': 'email', 'order_by': Guest.email, 'orderable': True, 'width': '12%', 'visible': 'yes'},
        {'name': 'Naam', 'data': 'full_name', 'order_by': Guest.child_last_name, 'orderable': True, 'width': '6%', 'visible': 'no'},
        {'name': 'Kind', 'data': 'child_name', 'order_by': Guest.child_first_name, 'orderable': True, 'width': '6%', 'visible': 'yes'},
        {'name': 'Geboortedatum', 'data': 'date_of_birth_dutch', 'order_by': Guest.date_of_birth, 'orderable': True, 'width': '6%', 'visible': 'yes'},
        {'name': 'Telefoon', 'data': 'phone', 'order_by': Guest.phone, 'orderable': True, 'width': '6%', 'visible': 'no'},
        {'name': 'Notitie', 'data': 'note', 'order_by': Guest.note, 'orderable': True, 'width': '20%', 'celledit': 'text', 'visible': 'yes'},
        {'name': 'R', 'data': 'reg_ack_email_tx', 'order_by': Guest.reg_ack_email_tx, 'width': '1%', 'celltoggle': 'standard', 'visible': 'no'},
        {'name': 'R', 'data': 'reg_ack_nbr_tx', 'order_by': Guest.reg_ack_nbr_tx, 'width': '1%', 'visible': 'no'},
        {'name': 'T', 'data': 'tsl_ack_email_tx', 'order_by': Guest.reg_ack_email_tx, 'width': '1%', 'celltoggle': 'standard', 'visible': 'no'},
        {'name': 'T', 'data': 'tsl_ack_nbr_tx', 'order_by': Guest.tsl_ack_email_tx, 'width': '1%', 'visible': 'no'},
        {'name': 'C', 'data': 'cancel_email_tx', 'order_by': Guest.cancel_email_tx, 'width': '1%', 'celltoggle': 'standard', 'visible': 'no'},
        {'name': 'C', 'data': 'cancel_nbr_tx', 'order_by': Guest.cancel_nbr_tx, 'width': '1%', 'visible': 'no'},
        {'name': 'A', 'data': 'enabled', 'order_by': Guest.enabled, 'width': '1%', 'celltoggle': 'standard', 'visible': 'yes'},
        {'name': 'T', 'data': 'email_tot_nbr_tx', 'order_by': Guest.email_tot_nbr_tx, 'orderable': True, 'celledit': 'int', 'width': '1%', 'visible': 'no'},
    ],
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'item': {
        'edit': {'title': 'Wijzig een gast', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        'add': {'title': 'Voeg een gast toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mguest.pre_filter,
    'format_data': mguest.format_data,
    'filter_data': mguest.filter_data,
    'search_data': mguest.search_data,
    'default_order': (1, 'asc'),
    'socketio_endpoint': 'celledit-registration',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
