from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from .forms import AddForm, EditForm, ViewForm
from app import db, log, admin_required, data
from . import user
from app.data.models import User

from app.presentation.layout import utils
from app.application import tables

from app.presentation.layout.utils import flash_plus, button_pressed

from app.presentation.view import base_multiple_items

@user.route('/user', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    return base_multiple_items.show(configuration)


@user.route('/user/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    return base_multiple_items.ajax(configuration)


@user.route('/user/table_action', methods=['GET', 'POST'])
@login_required
@admin_required
def table_action():
    if button_pressed('add'):
        return item_add()
    if button_pressed('edit'):
        return item_edit()
    if button_pressed('view'):
        return item_view()
    if button_pressed('delete'):
        return item_delete()


@user.route('/user/item_action/<string:action>', methods=['GET', 'POST'])
@login_required
@admin_required
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
    return redirect(url_for('user.show'))


def item_add(done=False):
    try:
        common_details = tables.prepare_item_config_for_view(configuration, 'add')
        if done:
            form = AddForm(request.form)
            if form.validate() and request.method == 'POST':
                if form.user_type.data == User.USER_TYPE.LOCAL:
                    password = form.password.data
                else:
                    password = ''
                user = User(email=form.email.data,username=form.username.data,first_name=form.first_name.data,last_name=form.last_name.data,
                            password=password,level=form.level.data,user_type=form.user_type.data)
                db.session.add(user)
                db.session.commit()
                log.info('add: {}'.format(user.log()))
                return redirect(url_for('user.show'))
            else:
                return render_template('user/user.html', form_details=form, common_details=common_details)
        else:
            form = AddForm()
            return render_template('user/user.html', form_details=form, common_details=common_details)
    except Exception as e:
        log.error(u'Could not add user {}'.format(e))
        flash_plus(u'Kan gebruikers niet toevoegen', e)
        db.session.rollback()
    return redirect(url_for('user.show'))


def item_edit(done=False, id=-1):
    try:
        common_details = tables.prepare_item_config_for_view(configuration, 'edit')
        if done:
            user = User.query.get(id)
            form = EditForm(request.form)
            if form.validate() and request.method == 'POST':
                form.populate_obj(user)
                db.session.commit()
                return redirect(url_for('user.show'))
            else:
                return render_template('user/user.html', form_details=form, common_details=common_details)
        else:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                id = int(chbx_id_list[0])  # only the first one can be edited
            if id > -1:
                user = User.query.get(id)
                form = EditForm(obj=user, formdata=None)
                common_details['item_id'] = id
            else:
                return redirect(url_for('user.show'))
            return render_template('user/user.html', form_details=form, common_details=common_details)
    except Exception as e:
        log.error(u'Could not edit user {}'.format(e))
        flash_plus(u'Kan gebruiker niet aanpassen', e)
    return redirect(url_for('user.show'))


def item_view(done=False, id=-1):
    try:
        common_details = tables.prepare_item_config_for_view(configuration, 'view')
        if done:
            pass
            # nothing to do)
        else:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                id = int(chbx_id_list[0])  # only the first one can be viewed
                user = User.query.get(id)
                form = ViewForm(obj=user, formdata=None)
                common_details['item_id'] = id
            else:
                return redirect(url_for('user.show'))
            return render_template('user/user.html', form_details=form, common_details=common_details)
    except Exception as e:
        log.error(u'Could not view user {}'.format(e))
        flash_plus(u'Kan gebruiker niet bekijken', e)
    return redirect(url_for('user.show'))


def item_delete():
    try:
        chbx_id_list = request.form.getlist('chbx')
        for id in chbx_id_list:
            if int(id) == 1:
                log.error(u'cannot delete this user')
                utils.flash_plus(u'Kan de gebruiker admin niet verwijderen')
                continue
            if int(id) == current_user.id:
                log.error(u'user cannot delete himself')
                utils.flash_plus(u'Een gebruiker kan niet zichzelf verwijderen.')
                continue
            user = User.query.get(int(id))
            db.session.delete(user)
        db.session.commit()
    except Exception as e:
        log.error(u'Could not delete user: {}'.format(e))
        utils.flash_plus(u'Kan de gebruikers niet verwijderen', e)
    return redirect(url_for('user.show'))


configuration = {
    'view': 'user',
    'title': 'Gebruikers',
    'buttons': ['delete', 'add', 'edit', 'view'],
    'delete_message': u'Wilt u deze gebruiker(s) verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'Gebruikersnaam', 'data': 'username', 'order_by': User.username, 'orderable': True},
        {'name': 'Voornaam', 'data': 'first_name', 'order_by': User.first_name, 'orderable': True},
        {'name': 'Naam', 'data': 'last_name', 'order_by': User.last_name, 'orderable': True},
        {'name': 'Email', 'data': 'email', 'order_by': User.email, 'orderable': True},
        {'name': 'Type', 'data': 'user_type', 'order_by': User.user_type, 'orderable': True},
        {'name': 'Login', 'data': 'last_login', 'order_by': User.last_login, 'orderable': True},
        {'name': 'Niveau', 'data': 'level', 'order_by': User.level, 'orderable': True}, ],
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
