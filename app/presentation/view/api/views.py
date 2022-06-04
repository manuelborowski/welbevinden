from flask import request
from . import api
from app.application import  student as mstudent, user as muser, photo as mphoto
from app.data import settings as msettings
from app import flask_app
import json
from functools import wraps


def key_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.values:
            api_key = request.values["api_key"]
        else:
            return json.dumps({"status": False, "data": f'Please provide a key'})
        # Check if API key is correct and valid
        if request.method == "POST" and api_key == flask_app.config['API_KEY']:
            return func(*args, **kwargs)
        else:
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
def photo_get(id):
    ret = mphoto.get_photo(id)
    return ret


@api.route('/api/vsknumber/get', methods=['GET'])
def get_last_vsk_number():
    ret = mstudent.get_last_vsk_number()
    return json.dumps(ret)


@api.route('/api/vsknumber/update', methods=['POST'])
def update_vsk_number():
    data = json.loads(request.data)
    ret = mstudent.update_vsk_numbers(int(data['start']))
    return json.dumps(ret)


@api.route('/api/vsknumber/clear', methods=['POST'])
def clear_vsk_numbers():
    ret = mstudent.clear_vsk_numbers()
    return json.dumps(ret)


