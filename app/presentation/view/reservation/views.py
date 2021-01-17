from . import reservation
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.data import reservation as mdreservation
from app.application import reservation as mreservation, settings as msettings
from app.data.models import SchoolReservation, AvailablePeriod
from app.presentation.layout.utils import flash_plus, button_pressed
from app.presentation.view import update_available_periods, false, true, null, prepare_registration_form

import json


@reservation.route('/reservation', methods=['POST', 'GET'])
def show():
    return base_multiple_items.show(table_configuration)


@reservation.route('/reservation/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration)


@reservation.route('/reservation/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    pass
    if button_pressed('edit'):
        return item_edit()


def item_edit(done=False, id=-1):
    try:
        chbx_id_list = request.form.getlist('chbx')
        if chbx_id_list:
            id = int(chbx_id_list[0])  # only the first one can be edited
        reservation = mreservation.get_reservation_by_id(id)
        config_data = prepare_registration_form(reservation.reservation_code)
        return render_template('end_user/register.html', config_data=config_data,
                               registration_endpoint = 'reservation.reservation_save')
    except Exception as e:
        log.error(f'could not edit reservation {request.args}: {e}')
        return redirect(url_for('reservation.show'))

@reservation.route('/reservation_save/<string:form_data>', methods=['POST', 'GET'])
@login_required
@supervisor_required
def reservation_save(form_data):
    try:
        data = json.loads(form_data)
        if data['cancel-reservation']:
            try:
                mreservation.delete_registration(data['reservation-code'])
            except Exception as e:
                flash_plus('Kon de reservatie niet verwijderen', e)
        else:
            try:
                ret = mreservation.add_or_update_registration(data, suppress_send_ack_email=True)
                if ret.result == ret.Result.E_NO_BOXES_SELECTED:
                    flash_plus('U hebt geen boxen geselecteerd',)
                if ret.result == ret.Result.E_OK:
                    flash_plus('Reservatie is aangepast')
                if ret.result == ret.Result.E_NOT_ENOUGH_BOXES:
                    flash_plus('Er zijn niet genoeg boxen')
            except Exception as e:
                flash_plus('Onbekende fout opgetreden', e)
    except Exception as e:
        flash_plus('Onbekende fout opgetreden', e)
    return redirect(url_for('reservation.show'))


table_configuration = {
    'view': 'reservation',
    'title': 'Reservaties',
    'buttons': [
        # 'delete', 'add', 'edit', 'view'
        'edit'
    ],
    'delete_message': u'Wilt u deze reservatie(s) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'School', 'data': 'name-school', 'order_by': SchoolReservation.name_school, 'orderable': True},
        {'name': 'Leerkracht 1', 'data': 'name-teacher-1', 'order_by': SchoolReservation.name_teacher_1,
         'orderable': True},
        {'name': 'Leerkracht 2', 'data': 'name-teacher-2', 'order_by': SchoolReservation.name_teacher_2,
         'orderable': True},
        {'name': 'Leerkracht 3', 'data': 'name-teacher-3', 'order_by': SchoolReservation.name_teacher_3,
         'orderable': True},
        {'name': 'Email', 'data': 'email', 'order_by': SchoolReservation.email, 'orderable': True},
        {'name': 'Tel', 'data': 'phone', 'order_by': SchoolReservation.phone, 'orderable': True},
        {'name': 'Adres', 'data': 'address', 'order_by': SchoolReservation.address, 'orderable': True},
        {'name': 'Postcode', 'data': 'postal-code', 'order_by': SchoolReservation.postal_code, 'orderable': True},
        {'name': 'Gemeente', 'data': 'city', 'order_by': SchoolReservation.city, 'orderable': True},
        {'name': 'Leerlingen', 'data': 'number-students', 'order_by': SchoolReservation.nbr_students,
         'orderable': True},
        {'name': 'Boxen', 'data': 'number-boxes', 'order_by': SchoolReservation.reservation_nbr_boxes,
         'orderable': True},
        {'name': 'Tijdslot', 'data': 'period', 'order_by': AvailablePeriod.date, 'orderable': True},
    ],
    'filter': [],
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mdreservation.pre_filter,
    'format_data': mdreservation.format_data,
    'search_data': mdreservation.search_data,
    'default_order': (1, 'asc'),
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
