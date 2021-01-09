from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import register
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import end_user as mend_user, room as mroom, utils as mutils, info_items as minfo_items

# @coworker.route('/coworker/<string:code>/<string:name>/<string:time>', methods=['POST', 'GET'])
# Check if room of coworker does not exist yet.  If so, create.
# Check if existing room is in state closed.  If so, delete room and create a new one
# Check if floor contains other, active, rooms of coworkers
@register.route('/register/new', methods=['POST', 'GET'])
def show():
    try:
        code = request.args['code']
        coworker = mend_user.get_end_user(code, set_timestamp=True)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'coworker with args {request.args} could not enter: {e}')
        return render_template('enduser/error.html', error='could_not_enter')
    return render_template('enduser/coworker/enter/coworker_enter.html', coworker=coworker.flat(),
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)


@enter.route('/coworker/enter/action/<string:jds>', methods=['GET', 'POST'])
def server_ajax_endpoint(jds):
    try:
        jd = json.loads(jds)
        if jd['action'] == 'get-timeout-1':
            return jsonify({"status": True})
    except Exception as e:
        log.error(f'execute action: {jd}')
        return jsonify({"status": False})

    return jsonify({"status": True})

