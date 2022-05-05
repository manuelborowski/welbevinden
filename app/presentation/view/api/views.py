from flask import request
from . import api
from app.application import registration as mregistration, student_care as mstudent, user as muser
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


@api.route('/api/student/add', methods=['POST'])
@key_required
def student_add():
    data = json.loads(request.data)
    ret = mstudent.add_student(data)
    return(json.dumps(ret))


@api.route('/api/student/update', methods=['POST'])
@key_required
def student_update():
    data = json.loads(request.data)
    ret = mstudent.update_student(data)
    return(json.dumps(ret))


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

@api.route('/api/register/add', methods=['POST', 'GET'])
def register_add():
    data = json.loads(request.data)
    ret = mregistration.registration_add(data)
    return(json.dumps(ret))


@api.route('/api/register/done', methods=['POST', 'GET'])
def register_done():
    data = json.loads(request.data)
    ret = mregistration.registration_done(data['code'])
    return(json.dumps({"status": True}))


@api.route('/api/register/update', methods=['POST', 'GET'])
def register_update():
    data = json.loads(request.data)
    ret = mregistration.registration_update(data['code'], data)
    return(json.dumps(ret))


@api.route('/api/register/status/check', methods=['POST', 'GET'])
def register_check():
    data = json.loads(request.data)
    ret = mregistration.check_register_status(data['code'])
    return(json.dumps(ret))


@api.route('/api/timeslot/add', methods=['POST', 'GET'])
def timeslot_add():
    data = json.loads(request.data)
    ret = mregistration.timeslot_add_registration(data)
    return(json.dumps(ret))


@api.route('/api/registers/info', methods=['POST', 'GET'])
def registers_get_info():
    if msettings.use_register():
        ret = mregistration.register_cache.get_registers_info()
        return(json.dumps(ret))
    else:
        return(json.dumps({'status': False, 'data': 'register not used'}))

