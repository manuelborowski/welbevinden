from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import end_user
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import end_user as mend_user, info_items as minfo_items, floor as mfloor

@end_user.route('/enter', methods=['POST', 'GET'])
def guest_enter():
    try:
        code = request.args['code']
        visit = mend_user.get_visit(code, set_timestamp=True)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'guest with args {request.args} could not enter: {e}')
        return render_template('end_user/error.html', error='could_not_enter')
    return render_template('end_user/end_user.html', user=visit.flat(), floors = mfloor.get_floors(),
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)
