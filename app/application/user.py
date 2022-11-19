from app import log
from app.data import user as muser, settings as msettings
from app.application.settings import subscribe_update_setting
import sys, json

def add_user(data):
    try:
        user = muser.get_first_user({'username': data['username']})
        if user:
            log.error(f'Error, user {user.username} already exists')
            return {"status": False, "data": f'Fout, gebruiker {user.username} bestaat al'}
        user = muser.add_user(data)
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
        user = muser.get_first_user({'id': data['id']})
        if user:
            del data['id']
            user = muser.update_user(user, data)
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
    muser.delete_users(ids)


############## formio forms #############
def prepare_add_registration_form():
    try:
        template = msettings.get_configuration_setting('user-formio-template')
        return {'template': template,
                'defaults': {'new_password': True}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_registration_form(id):
    try:
        user = muser.get_first_user({"id": id})
        template = msettings.get_configuration_setting('user-formio-template')
        return {'template': template,
                'defaults': user.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e



############ datatables: user overview list #########
def format_data(db_list, total_count, filtered_count):
    out = []
    for i in db_list:
        em = i.to_dict()
        em['row_action'] = f"{i.id}"
        em['DT_RowId'] = f"{i.id}"
        out.append(em)
    return total_count, filtered_count, out


def generate_users(setting, value, opaque):
    try:
        if setting == "user-generate-users":
            data = json.loads(value)
            for nu in data:
                user = muser.get_first_user({'username': nu['username']})
                if not user:
                    user = muser.add_user({"username": nu["username"], "password": nu["password"], "level": nu["level"], "user_type": "local"})
                    if user:
                        log.info(f"{sys._getframe().f_code.co_name}, added user {user.username}")
                    else:
                        log.error(f"{sys._getframe().f_code.co_name}, could not add user {nu['username']}")
                else:
                    log.error(f"{sys._getframe().f_code.co_name}, user {nu['username']} already exists")
            return False
        return True
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


subscribe_update_setting("user-generate-users", generate_users, None)