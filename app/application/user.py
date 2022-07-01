from app import log
from app.application import formio as mformio
from . import app
import sys

def add_user(data):
    try:
        user = app.data.user.get_first_user({'username': data['username']})
        if user:
            log.error(f'Error, user {user.username} already exists')
            return {"status": False, "data": f'Fout, gebruiker {user.username} bestaat al'}
        user = app.data.user.add_user(data)
        if 'confirm_password' in data:
            del data['confirm_password']
        if 'password' in data:
            del data['password']
        log.info(f"Add user: {data}")
        return {"status": True, "data": {'id': user.id}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def update_user(data):
    try:
        user = app.data.user.get_first_user({'id': data['id']})
        if user:
            del data['id']
            user = app.data.user.update_user(user, data)
            if user:
                if 'confirm_password' in data:
                    del data['confirm_password']
                if 'password' in data:
                    del data['password']
                log.info(f"Update user: {data}")
                return {"status": True, "data": {'id': user.id}}
        return {"status": False, "data": "Er is iets fout gegaan"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def delete_users(ids):
    app.data.user.delete_users(ids)


############## formio forms #############
def prepare_add_registration_form():
    try:
        template = app.data.settings.get_json_coded_setting('user-formio-template')
        return {'template': template,
                'defaults': {'new_password': True}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_registration_form(id):
    try:
        user = app.data.user.get_first_user({"id": id})
        template = app.data.settings.get_json_coded_setting('user-formio-template')
        template = mformio.prepare_for_edit(template, user.to_dict())
        return {'template': template,
                'defaults': user.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


