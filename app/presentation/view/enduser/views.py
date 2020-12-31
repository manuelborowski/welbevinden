from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import enduser
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import enduser as menduser

# @guest.route('/guest/<string:code>/<string:name>/<string:time>', methods=['POST', 'GET'])
@enduser.route('/enter', methods=['POST', 'GET'])
def show():
    try:
        code = request.args['code']
        user = menduser.get_end_user(code)
        if user.profile in [menduser.Profile.E_GAST, menduser.Profile.E_SCHOOL]:
            u = redirect(url_for('guest.enter.show', code=code))
            log.info(u.data)
            return u
        else:
            u = redirect(url_for('coworker.enter.show', code=code))
            log.info(u.data)
            return u
    except Exception as e:
        log.error(f'coworker with args {request.args} could not enter: {e}')
    return render_template('enduser/error.html', error='could_not_enter')


