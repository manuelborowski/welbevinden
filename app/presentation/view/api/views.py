from flask import request
from . import api
from app.application import registration as mregistration
import json


@api.route('/api/register/add', methods=['POST', 'GET'])
def register_add():
    data = json.loads(request.data)
    ret = mregistration.registration_add(data)
    return(json.dumps(ret))


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


