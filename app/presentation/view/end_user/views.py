from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import end_user
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import end_user as mend_user, info_items as minfo_items, floor as mfloor, visit as mvisit

@end_user.route('/enter', methods=['POST', 'GET'])
def enter():
    try:
        code = request.args['code']
        visit = mend_user.get_visit(code, set_timestamp=True)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'end user with args {request.args} could not enter: {e}')
        return render_template('end_user/error.html', error='could_not_enter')
    return render_template('end_user/end_user.html', user=visit.flat(), floors = mfloor.get_floors(),
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)


@end_user.route('/register', methods=['POST', 'GET'])
def register():
    try:
        register_for = request.args['for'] # guest, floor or fair
        if register_for == mend_user.Profile.E_GUEST:
            timeslots = mvisit.get_timeslots()
            return render_template('end_user/register.html', timeslots=timeslots)
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('end_user/error.html', error='could_not_register')


@end_user.route('/register_save', methods=['POST', 'GET'])
def register_save():
    pass