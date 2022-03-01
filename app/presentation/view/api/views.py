from flask import request
from . import api
from app.application import registration as mregistration
import json


@api.route('/api/register/add', methods=['POST', 'GET'])
def register_add():
    data = json.loads(request.data)
    ret = mregistration.add_registration(data)
    return(json.dumps(ret))


@api.route('/register/update', methods=['POST', 'GET'])
def register_update():
    data = json.loads(request.data)
    ret = mregistration.update_registration(data['code'], data)
    return(json.dumps(ret))


