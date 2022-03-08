from flask import render_template, request
from . import guest
from app import log
from app.application import email as memail, registration as mregistration
import re


@guest.route('/guest/get_form', methods=['POST', 'GET'])
def get_form():
    try:
        if request.values['form'] == 'register':
            data = mregistration.prepare_registration()
            data.update({
                'post_data_endpoint': 'api.register_add',
                'form_on_submit': 'register-done',
                'cancel_endpoint': 'guest.register'
            })
        elif request.values['form'] == 'register-done':
            data = mregistration.registration_done(request.values['extra'])
            data.update({
                'form_on_submit': 'register'
            })
        elif request.values['form'] == 'confirmation-document':
            data = mregistration.get_confirmation_document(request.values['extra'])
            data.update({
                'form_on_submit': 'register'
            })
        elif request.values['form'] == 'timeslot':
            data = mregistration.prepare_timeslot_registration(request.values['extra'])
            data.update({
                'post_data_endpoint': 'api.register_update',
                'form_on_submit': 'timeslot-register-done'
            })
        elif request.values['form'] == 'timeslot-register-done':
            data = mregistration.timeslot_registration_done(request.values['extra'])
            data.update()
        else:
            return {"status": False, "data": f"get_form: niet gekende form: {request.values['form']}"}
        return {"status": True, "data": data}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}


@guest.route('/guest/register', methods=['POST', 'GET'])
def register():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        return render_template('guest/render_formio.html', data={"form": "register", "get_form_endpoint": "guest.get_form"})
    except Exception as e:
        message = f'could not display registration form {request.args}: {e}'
        log.error(message)
        return render_template('errors/500.html', message=message)


@guest.route('/guest/get_confirmation_document', methods=['POST', 'GET'])
def get_confirmation_document():
    try:
        return render_template('guest/render_formio.html', data={"form": "confirmation-document",
                                                                 "extra": request.values["code"],
                                                                 "get_form_endpoint": "guest.get_form"})
    except Exception as e:
        message = f'could not get confirmation document form {request.args}: {e}'
        log.error(message)
        return render_template('errors/500.html', message=message)


@guest.route('/timeslot/register', methods=['POST', 'GET'])
def register_timeslot():
    try:
        code = request.values['code'] if 'code' in request.values else ""
        return render_template('guest/render_formio.html',
                               data={"form": "timeslot",
                                     "get_form_endpoint": "guest.get_form",
                                     "extra": code})
    except Exception as e:
        message = f'could not display timeslot registration form {request.args}: {e}'
        log.error(message)
        return render_template('errors/500.html', message=message)


