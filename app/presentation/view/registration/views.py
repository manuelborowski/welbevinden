from . import registration
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.presentation.layout.utils import flash_plus, button_pressed
from app.data import guest as mguest
from app.application import socketio as msocketio, registration as mregistration, guest as maguest, settings as msettings
from app.data.models import Guest
from app.application import tables

import json


@registration.route('/registration', methods=['POST', 'GET'])
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
    if button_pressed('update_registration'):
        return update_registration()
    return redirect(url_for('registration.show'))


@registration.route('/registration/item_action/<string:action>', methods=['GET', 'POST'])
@login_required
@supervisor_required
def item_action(action=None):
    try:
        id = int(request.values['item-id'])
    except:
        id = -1
    if button_pressed('save'):
        if action == 'add':
            return item_add(done=True)
        if action == 'edit':
            return item_edit(done=True, id=id)
    if button_pressed('edit'):
        if action == 'view':
            return item_edit(False, id)
    return redirect(url_for('registration.show'))


def item_delete(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        ids = [int(i) for i in chbx_id_list]
        mguest.delete_guest(ids)
    except Exception as e:
        log.error(f'could not delete guest {request.args}: {e}')
    return redirect(url_for('registration.show'))


def update_registration(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        if chbx_id_list:
            id = int(chbx_id_list[0])  # only the first one can be edited
        guest = mguest.get_first_guest(id=id)
        return redirect(url_for('guest.register', code=guest.code))
    except Exception as e:
        log.error(f'could not edit registration {request.args}: {e}')
    return redirect(url_for('registration.show'))


def get_form(extra_fields, default_values={}):
    form = {
        'fields': ['full_name', 'child_name', 'email', 'phone'],
        'config': {
            'full_name': {'label': 'Naam ouder', 'default': ''},
            'child_name': {'label': 'Naam kind', 'default': ''},
            'email': {'label': 'E-mail', 'default': ''},
            'phone': {'label': 'Telefoon', 'default': ''},
        }
    }
    for field in extra_fields:
        form['fields'].append(field)
        form['config'][field] = {'label': field, 'default': ''}
    if default_values:
        for field in form['fields']:
            form['config'][field]['default'] = default_values[field]
    return form


def get_misc_fields(extra_fields, form):
    misc_field = {}
    for field in extra_fields:
        if field in form:
            misc_field[field] = form[field]
    return misc_field


def item_edit(done=False, id=-1):
    try:
        misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
        extra_fields = [c['veldnaam'] for c in misc_config]
        common_details = tables.prepare_item_config_for_view(table_configuration, 'edit')
        if done:
            misc_field = get_misc_fields(extra_fields, request.form)
            guest = mguest.get_first_guest(id=id)
            guest = mguest.update_guest(guest, full_name=request.form['full_name'],
                                        child_name=request.form['child_name'], phone=request.form['phone'],
                                        email=request.form['email'], misc_field=json.dumps(misc_field))
            return redirect(url_for('registration.show'))
        else:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                id = int(chbx_id_list[0])  # only the first one can be edited
            if id > -1:
                guest = mguest.get_first_guest(id=id)
                form = get_form(extra_fields, guest.flat())
                common_details['item_id'] = id
            else:
                return redirect(url_for('registration.show'))
            return render_template('registration/registration.html', form_details=form, common_details=common_details)
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('registration.show'))


def item_add(done=False):
    try:
        misc_config = json.loads(msettings.get_configuration_setting('import-misc-fields'))
        extra_fields = [c['veldnaam'] for c in misc_config]
        if done:
            misc_field = get_misc_fields(extra_fields, request.form)
            guest = maguest.add_guest(full_name=request.form['full_name'], email=request.form['email'])
            guest = mguest.update_guest(guest, child_name=request.form['child_name'], phone=request.form['phone'],
                                        misc_field=json.dumps(misc_field))
            log.info(f'add: {guest.email}')
            return redirect(url_for('registration.show'))
        else:
            common_details = tables.prepare_item_config_for_view(table_configuration, 'add')
            form = get_form(extra_fields)
            return render_template('registration/registration.html', form_details=form,
                                   common_details=common_details)
    except Exception as e:
        log.error(f'Could not add guest {e}')
        flash_plus(f'Kan gebruiker niet toevoegen: {e}')
    return redirect(url_for('registration.show'))


@registration.route('/registration_save/<string:form_data>', methods=['POST', 'GET'])
@login_required
@supervisor_required
def registration_save(form_data):
    try:
        data = json.loads(form_data)
        if 'cancel-registration' in data and data['cancel-registration']:
            try:
                mregistration.delete_registration(data['registration-code'])
                flash_plus('Reservatie is verwijderd')
            except Exception as e:
                flash_plus('Kon de reservatie niet verwijderen', e)
        else:
            try:
                ret = mregistration.add_or_update_registration(data)
                if ret.result == ret.Result.E_OK:
                    flash_plus('Reservatie is aangepast')
                if ret.result == ret.Result.E_TIMESLOT_FULL:
                    flash_plus('Op dit tijdslot zijn er geen plaatsen meer beschikbaar')
            except Exception as e:
                flash_plus('Onbekende fout opgetreden', e)
    except Exception as e:
        flash_plus('Onbekende fout opgetreden', e)
    return redirect(url_for('registration.show'))


def registration_update_cb(value, opaque):
    msocketio.broadcast_message({'type': 'celledit-registration', 'data': {'reload-table': True}})


mregistration.subscribe_registration_changed(registration_update_cb, None)


def celledit_event_cb(msg, client_sid=None):
    if msg['data']['column'] == 6:
        mregistration.update_registration('note', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 7:
        mregistration.update_registration('invite_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 9:
        mregistration.update_registration('ack_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 11:
        mregistration.update_registration('cancel_email_sent', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 13:
        mregistration.update_registration('enabled', msg['data']['id'], msg['data']['value'])
    if msg['data']['column'] == 14:
        mregistration.update_registration('email_send_retry', msg['data']['id'], msg['data']['value'])
    msocketio.send_to_room({'type': 'celledit-registration', 'data': {'status': True}}, client_sid)


msocketio.subscribe_on_type('celledit-registration', celledit_event_cb)


def get_filters():
    return [
        {
            'type': 'select',
            'name': 'timeslot',
            'label': 'Reservatie',
            'choices': [
                ['default', 'Alles'],
                ['yes', 'Gemaakt'],
                ['no', 'Open'],
            ],
            'default': 'default',
        },
    ]


def get_show_info():
    nbr_total, nbr_open, nbr_reserved = mregistration.get_registration_counters()
    return [
        f'Totaal: {nbr_total}',
        f'Open: {nbr_open}',
        f'Gereserveerd: {nbr_reserved}',
    ]


table_configuration = {
    'view': 'registration',
    'title': 'Gasten',
    'buttons': ['edit', 'add', 'delete', 'update_registration'],
    'delete_message': 'Opgelet!!<br>'
                      'Bent u zeker om deze gast(en) verwijderen?<br>'
                      'Eens verwijderd kunnen ze niet meer worden terug gehaald.<br>'
                      'Indien u de reservatie wilt verwijderen, kies dan <b>Wijzig</'
                      'b> en annuleer dan de reservatie.',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '1%', 'visible': 'never'},
        {'name': 'TijdStempel', 'data': 'register_timestamp_dutch', 'order_by': Guest.register_timestamp, 'orderable': True, 'width': '8%', 'visible': True},
        {'name': 'R', 'data': 'register', 'order_by': Guest.field_of_study, 'orderable': True, 'width': '2%', 'visible': True},
        {'name': 'I', 'data': 'indicator_dutch', 'order_by': Guest.indicator, 'orderable': True, 'width': '1%', 'className': 'dt-center', 'visible': True},
        {'name': 'Tijdslot', 'data': 'timeslot', 'order_by': Guest.timeslot, 'orderable': True, 'width': '8%', 'visible': True},
        {'name': 'Email', 'data': 'email', 'order_by': Guest.email, 'orderable': True, 'width': '12%', 'visible': True},
        {'name': 'Naam', 'data': 'full_name', 'order_by': Guest.child_last_name, 'orderable': True, 'width': '6%', 'visible': True},
        {'name': 'Kind', 'data': 'child_name', 'order_by': Guest.child_first_name, 'orderable': True, 'width': '6%', 'visible': True},
        {'name': 'Telefoon', 'data': 'phone', 'order_by': Guest.phone, 'orderable': True, 'width': '6%', 'visible': True},
        {'name': 'Notitie', 'data': 'note', 'order_by': Guest.note, 'orderable': True, 'width': '20%',
         'celledit': 'text', 'visible': True},
        {'name': 'U', 'data': 'invite_email_sent', 'order_by': Guest.invite_email_tx, 'width': '1%',
         'celltoggle': 'standard', 'visible': True},
        {'name': 'U', 'data': 'nbr_invite_sent', 'order_by': Guest.invite_nbr_tx, 'width': '1%', 'visible': True},
        {'name': 'B', 'data': 'ack_email_sent', 'order_by': Guest.reg_ack_email_tx, 'width': '1%',
         'celltoggle': 'standard', 'visible': True},
        {'name': 'B', 'data': 'nbr_ack_sent', 'order_by': Guest.reg_ack_nbr_tx, 'width': '1%', 'visible': True},
        {'name': 'C', 'data': 'cancel_email_sent', 'order_by': Guest.cancel_email_tx, 'width': '1%',
         'celltoggle': 'standard', 'visible': True},
        {'name': 'C', 'data': 'nbr_cancel_sent', 'order_by': Guest.cancel_nbr_tx, 'width': '1%', 'visible': True},
        {'name': 'A', 'data': 'enabled', 'order_by': Guest.enabled, 'width': '1%', 'celltoggle': 'standard', 'visible': True},
        {'name': 'R', 'data': 'email_send_retry', 'order_by': Guest.email_tot_nbr_tx, 'orderable': True,
         'celledit': 'text', 'width': '1%', 'visible': True},
    ],
    'get_filters': get_filters,
    'get_show_info': get_show_info,
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
