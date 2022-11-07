import datetime

from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app import log, admin_required, data, flask_app
from . import user
from app.application import user as muser
from app.presentation.layout.utils import flash_plus
from app.presentation.view import datatables
import json
from app.data.datatables import DatatableConfig
import app.data.user
import app.application.user

@user.route('/user', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    # start = datetime.datetime.now()
    ret = datatables.show(table_configuration)
    # print('student.show', datetime.datetime.now() - start)
    return ret


@user.route('/user/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    ret =  datatables.ajax(table_configuration)
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
    return redirect(url_for('user.show'))


item_common = {'post_data_endpoint': 'api.user_update', 'submit_endpoint': 'user.show', 'cancel_endpoint': 'user.show', 'api_key': flask_app.config['API_KEY']}


@admin_required
def item_add():
    try:
        data = muser.prepare_add_registration_form()
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning"), ("clear-ack", "Velden wissen", "warning")]})
        data['post_data_endpoint'] = 'api.user_add'
        return render_template('user/s_user.html', data=data)
    except Exception as e:
        log.error(f'Could not add user {e}')
        flash_plus(f'Kan gebruiker niet toevoegen: {e}')
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
        data = muser.prepare_edit_registration_form(id)
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning")]})
        return render_template('user/s_user.html', data=data)
    except Exception as e:
        log.error(f'Could not edit user {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('user.show'))


@user.route('/user/right_click/', methods=['POST', 'GET'])
@admin_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "delete":
                    muser.delete_users(data['item_ids'])
                    return {"message": "gebruikers zijn verwijderd, ververs het browserscherm"}
                if data['item'] == "add":
                    return {"redirect": {"url": f"/user/table_action/add"}}
                if data['item'] == "edit":
                    return {"redirect": {"url": f"/user/table_action/edit", "ids": data['item_ids']}}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}
    return {"status": False, "data": "iets is fout gelopen"}


class UserConfig(DatatableConfig):
    def pre_sql_query(self):
        return app.data.user.pre_sql_query()

    def pre_sql_search(self, search):
        return data.user.pre_sql_search(search)

    def get_right_click(self):
        return {
            'endpoint': 'user.right_click',
            'menu': [
                {'label': 'Nieuwe gebruiker', 'item': 'add', 'iconscout': 'plus-circle'},
                {'label': 'Gebruiker aanpassen', 'item': 'edit', 'iconscout': 'pen'},
                {'label': 'Gebruiker(s) verwijderen', 'item': 'delete', 'iconscout': 'trash-alt', 'ack': 'Bent u zeker dat u deze gebruiker(s) wilt verwijderen?'},
            ]
        }

    def format_data(self, l, count):
        return app.application.user.format_data(l, count)

table_configuration = UserConfig("user", "Gebruikers")

