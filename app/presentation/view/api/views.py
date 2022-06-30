from flask import request
from . import api
from app.application import  student as mstudent, user as muser, photo as mphoto, staff as mstaff
from app.data import settings as msettings
from app import flask_app, log
import json, sys
from functools import wraps


def key_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            if request.headers.get('x-api-key') == flask_app.config['API_KEY']:
                return func(*args, **kwargs)
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": f'Key not valid'})
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


@api.route('/api/photo/get/<int:id>', methods=['GET'])
@key_required
def photo_get(id):
    ret = mphoto.get_photo(id)
    return ret


@api.route('/api/vsknumber/get', methods=['GET'])
@key_required
def get_last_vsk_number():
    ret = mstudent.get_next_vsk_number()
    return json.dumps(ret)


@api.route('/api/vsknumber/update', methods=['POST'])
@key_required
def update_vsk_number():
    data = json.loads(request.data)
    ret = mstudent.update_vsk_numbers(int(data['start']))
    return json.dumps(ret)


@api.route('/api/vsknumber/clear', methods=['POST'])
@key_required
def clear_vsk_numbers():
    ret = mstudent.clear_vsk_numbers()
    return json.dumps(ret)


@api.route('/api/fields/<string:table>', methods=['GET'])
@key_required
def get_fields(table):
    ret = 'table not found'
    if table == 'student':
        ret = mstudent.get_fields()
    if table == 'staff':
        ret = mstaff.get_fields()
    return json.dumps(ret)


@api.route('/api/students/', methods=['GET'])
@key_required
def get_students():
    options = request.args
    ret = mstudent.get_students(options)
    return json.dumps(ret)

@api.route('/api/staff/', methods=['GET'])
@key_required
def get_staff():
    options = request.args
    ret = mstaff.get_staffs(options)
    return json.dumps(ret)


# ?fields=klasgroep,schooljaar
# sort=-gemeente
# gemeente=nijlen   filter on gemeente equals nijlen

