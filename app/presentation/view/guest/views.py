from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context, request
from flask_login import login_required, current_user
from . import end_user
from app import log, socketio, admin_required
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import guest as mguest, email as memail
import json, re
from app.presentation.view import update_available_timeslots, false, true, null, prepare_registration_form

@end_user.route('/register', methods=['POST', 'GET'])
def register():
    try:
        current_url = request.url
        current_url = re.sub(f'{request.url_rule.rule}.*', '', current_url)
        memail.set_base_url(current_url)
        code = request.args['code'] if 'code' in request.args else None
        config_data = prepare_registration_form(code)
        return render_template('guest/register.html', config_data=config_data,
                               registration_endpoint = 'guest.register_save')
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('guest/messages.html', type='unknown-error', message=e)


@end_user.route('/register_save/<string:form_data>', methods=['POST', 'GET'])
def register_save(form_data):
    try:
        data = json.loads(form_data)
        # if data['cancel-reservation']:
        #     try:
        #         mreservation.delete_registration(data['reservation-code'])
        #         return render_template('guest/messages.html', type='cancel-ok')
        #     except Exception as e:
        #         return render_template('guest/messages.html', type='could-not-cancel', message=e)
        # else:
        #     try:
        #         ret = mreservation.add_or_update_registration(data)
        #         if ret.result == ret.Result.E_NO_BOXES_SELECTED:
        #             return render_template('guest/messages.html', type='no-boxes-selected')
        #         if ret.result == ret.Result.E_OK:
        #             info = {'school': ret.reservation['name-school'], 'period': ret.reservation['period'], 'nbr_boxes': ret.reservation['number-boxes']}
        #             return render_template('guest/messages.html', type='register-ok', info=info)
        #         if ret.result == ret.Result.E_NOT_ENOUGH_BOXES:
        #             return render_template('guest/messages.html', type='not-enough-boxes')
        #     except Exception as e:
        #         return render_template('guest/messages.html', type='could-not-register', message=e)
        #     return render_template('guest/messages.html', type='could-not-register')
    except Exception as e:
        return render_template('guest/messages.html', type='unknown-error', message=e)


register_formio = \
    {}
