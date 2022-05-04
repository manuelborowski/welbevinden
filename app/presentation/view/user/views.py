from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app import log, admin_required, data, flask_app
from . import user
from app.application import user as muser
from app.presentation.layout.utils import flash_plus
from app.presentation.view import base_multiple_items
import json

@user.route('/user', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret = base_multiple_items.show(table_configuration)
    # print('student.show', datetime.datetime.now() - start)
    return ret


@user.route('/user/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    base_multiple_items.update(table_configuration)
    ret =  base_multiple_items.ajax(table_configuration)
    # print('student.table_ajax', datetime.datetime.now() - start)
    return ret


@user.route('/user/table_action', methods=['GET', 'POST'])
@user.route('/user/table_action/<string:action>', methods=['GET', 'POST'])
@user.route('/user/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
@admin_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    if action == 'delete':
        return item_delete(ids)
    return redirect(url_for('user.show'))


@user.route('/user/get_form', methods=['POST', 'GET'])
@admin_required
def get_form():
    try:
        common = {
            'post_data_endpoint': 'api.user_update',
            'submit_endpoint': 'user.show',
            'cancel_endpoint': 'user.show',
            'api_key': flask_app.config['API_KEY']
        }
        if request.values['form'] == 'edit':
            data = muser.prepare_edit_registration_form(request.values['extra'])
            data.update(common)
        elif request.values['form'] == 'add':
            data = muser.prepare_add_registration_form()
            data.update(common)
            data['post_data_endpoint'] = 'api.user_add'
        else:
            return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
        return {"status": True, "data": data}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}


@admin_required
def item_add():
    try:
        return render_template('render_formio.html', data={"form": "add",
                                                           "get_form_endpoint": "user.get_form"})
    except Exception as e:
        log.error(f'Could not add user {e}')
        flash_plus(f'Kan gebruiker niet toevoegen: {e}')
    return redirect(url_for('user.show'))


@admin_required
def item_delete(ids=None):
    try:
        if ids == None:
            ids = request.form.getlist('chbx')
        muser.delete_users(ids)
    except Exception as e:
        log.error(f'could not delete user {request.args}: {e}')
    return redirect(url_for('user.show'))


@admin_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('user.show'))
        else:
            id = ids[0]
        return render_template('render_formio.html', data={"form": "edit",
                                                           "get_form_endpoint": "user.get_form",
                                                            "extra": id})
    except Exception as e:
        log.error(f'Could not edit user {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('user.show'))




table_configuration = {
    'view': 'user',
    'title': 'Gebruikers',
    'buttons': ['delete', 'add', 'edit'],
    'delete_message': u'Wilt u deze gebruiker(s) verwijderen?',
    'filter': [],
    'item': {
        'edit': {'title': 'Wijzig een gebruiker', 'buttons': ['save', 'cancel']},
        'view': {'title': 'Bekijk een gebruiker', 'buttons': ['edit', 'cancel']},
        'add': {'title': 'Voeg een gebruiker toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': data.user.pre_filter,
    'format_data': data.user.format_data,
    'search_data': data.user.search_data,
    'default_order': (1, 'asc'),
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
