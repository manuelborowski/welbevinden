from flask import request
from . import api
from app.application import  student as mstudent, user as muser
from app.data import settings as msettings
from app import flask_app, log
import json, sys, html
from functools import wraps


def key_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            keys = msettings.get_configuration_setting('api-keys')
            if request.headers.get('x-api-key') in keys:
                return func(*args, **kwargs)
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            return json.dumps({"status": False, "data": e})
        return json.dumps({"status": False, "data": f'API key not valid'})
    return decorator


@api.route('/api/user/add', methods=['POST'])
@key_required
def user_add():
    data = json.loads(request.data)
    ret = muser.add_user(data)
    return(json.dumps(ret))


@api.route('/api/user/update', methods=['POST'])
@key_required
def user_update():
    data = json.loads(request.data)
    ret = muser.update_user(data)
    return(json.dumps(ret))


