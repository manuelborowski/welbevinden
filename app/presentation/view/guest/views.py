from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context, request, make_response
from flask_login import login_required, current_user
from . import guest
from app import log, socketio, admin_required
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import guest as mguest, email as memail, registration as mregistration
import json, re, urllib
from app.presentation.view import update_available_timeslots, false, true, null, prepare_registration_form


@guest.route('/register', methods=['POST', 'GET'])
def register():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        ret = mregistration.prepare_registration()
        ret.data['submit'] = {'endpoint': 'guest.register_save', 'data': True}
        return render_template('guest/render_formio.html', data=ret.data)
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('guest/messages.html', type='unknown-error', message=e)


@guest.route('/register_save/<string:form_data>', methods=['POST', 'GET'])
def register_save(form_data):
    try:
        data = json.loads(urllib.parse.unquote(form_data))
        try:
            ret = mregistration.add_registration(data)
            ret.data['submit'] = {'endpoint': 'guest.register', 'data': False}
            return render_template('guest/render_formio.html', data=ret.data)
        except Exception as e:
            return render_template('guest/messages.html', type='could-not-register', message=e)
        return render_template('guest/messages.html', type='could-not-register')
    except Exception as e:
        return render_template('guest/messages.html')


@guest.route('/get_confirmation_document', methods=['POST', 'GET'])
def get_confirmation_document():
    code = request.args['code'] if 'code' in request.args else None
    ret = mregistration.get_confirmation_document(code)
    return render_template('guest/render_formio.html', data=ret.data)



@guest.route('/register_timeslot', methods=['POST', 'GET'])
def register_timeslot():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        code = request.args['code'] if 'code' in request.args else None
        ret = prepare_registration_form(code)
        if ret.result == ret.Result.E_COULD_NOT_REGISTER:
            return render_template('guest/messages.html', type='could-not-register')
        if ret.result == ret.Result.E_NO_TIMESLOT:
            return render_template('guest/messages.html', type='no-timeslot')
        return render_template('guest/render_formio.html', config_data=ret.data,
                               registration_endpoint='guest.register_save')
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('guest/messages.html', type='unknown-error', message=e)


@guest.route('/register_timeslot_save/<string:form_data>', methods=['POST', 'GET'])
def register_timeslot_save(form_data):
    try:
        data = json.loads(urllib.parse.unquote(form_data))
        if 'cancel-registration' in data and data['cancel-registration']:
            try:
                mregistration.delete_registration(data['registration-code'])
                return render_template('guest/messages.html', type='cancel-ok')
            except Exception as e:
                return render_template('guest/messages.html', type='could-not-cancel', message=e)
        else:
            try:
                ret = mregistration.add_or_update_registration(data)
                if ret.result == ret.Result.E_OK:
                    return render_template('guest/messages.html', type='register-ok', info=ret.data)
                if ret.result == ret.Result.E_TIMESLOT_FULL:
                    return render_template('guest/messages.html', type='timeslot-full', info=ret.data)
            except Exception as e:
                return render_template('guest/messages.html', type='could-not-register', message=e)
            return render_template('guest/messages.html', type='could-not-register')
    except Exception as e:
        return render_template('guest/messages.html', type='unknown-error', message=e)


