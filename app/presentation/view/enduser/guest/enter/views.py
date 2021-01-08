from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import enter
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import enduser as menduser, info_items as minfo_items

# @guest.route('/guest/<string:code>/<string:name>/<string:time>', methods=['POST', 'GET'])
@enter.route('/guest/enter', methods=['POST', 'GET'])
def show():
    try:
        code = request.args['code']
        guest = menduser.get_end_user(code, set_timestamp=True)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'guest with args {request.args} could not enter: {e}')
        return render_template('enduser/error.html', error='could_not_enter')
    return render_template('enduser/guest/enter/enter.html', guest=guest.flat(),
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)





