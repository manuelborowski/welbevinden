from app.data.models import EndUser
from app.data import utils as mutils
import random, string, datetime
from app import log, db
from app.application import socketio as msocketio, room as mroom, settings as msettings

allowed_chars = string.ascii_letters + string.digits
def create_random_string(len):
    return ''.join(random.choice(allowed_chars) for i in range(len))


class Profile(EndUser.Profile):
    pass

def add_end_user(first_name, last_name, email, profile, timeslot=None, code=None):
    try:
        user = EndUser.query.filter(EndUser.first_name == first_name, EndUser.last_name == last_name,
                                    EndUser.email == email, EndUser.profile == profile).first()
        if user:
            log.warning(f'Enduser {user.full_name()} already exists')
            return False
        if not code:
            code = create_random_string(32)
        if not timeslot:
            timeslot = datetime.datetime.now()
        user = EndUser(first_name=first_name, last_name=last_name, email=email, profile=profile, code=code,
                       timeslot=timeslot)
        db.session.add(user)
        db.session.commit()
        log.info(f'Enduser {user.full_name()} added')
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return True


def get_end_user(code, set_timestamp=False):
    try:
        user = EndUser.query.filter(EndUser.code == code).first()
        if set_timestamp:
            user.last_login = datetime.datetime.now()
        return user
    except Exception as e:
        mutils.raise_error('could not find end user', e)
    return None


def get_end_user_by_socketio(socketio_sid):
    try:
        user = EndUser.query.filter(EndUser.socketio_sid == socketio_sid).first()
        return user
    except Exception as e:
        mutils.raise_error('could not find end user', e)
    return None


def set_socketio_sid(user_code, sid):
    try:
        user = EndUser.query.filter(EndUser.code == user_code).first()
        sid_valid = user.socketio_sid is not None
        user.socketio_sid = sid
        db.session.commit()
        user.user_already_logged_in = sid_valid
        log.info(f'Enduser {user.full_name()} logged in')
        return user
    except Exception as e:
        mutils.raise_error(f'could not set socketio_sid {user_code} {sid}', e)


def remove_socketio_sid_cb(msg, sid):
    try:
        user = EndUser.query.filter(EndUser.socketio_sid == sid).first()
        if user:
            user.socketio_sid = None
            db.session.commit()
            log.info(f'Enduser {user.full_name()} logged out')
        else:
            log.warning(f'Enduser with sid {sid} not found (enduser probably refreshed page)')
    except Exception as e:
        mutils.raise_error(f'could not remove socketio_sid {sid}', e)


msocketio.subscribe_on_type('disconnect', remove_socketio_sid_cb)


def new_end_user_cb(msg, client_sid):
    user = set_socketio_sid(msg['data']['user_code'], client_sid)
    if user.profile == EndUser.Profile.E_SCHOOL:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
    elif user.profile == EndUser.Profile.E_GAST:
        room = mroom.select_least_occupied_room(EndUser.Profile.E_CLB)
        room_owner = get_end_user(room.code)
        add_chatroom(EndUser.Profile.E_CLB, room.code, room_owner.full_name(), client_sid)
        send_chat_history(room.code, client_sid)
        send_time_when_to_show_stage(2, user)
    else:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
        add_chatroom(user.profile, user.code, user.full_name(), client_sid)
        send_chat_history(msg['data']['user_code'], client_sid)


def show_stage(stage, sid):
    msocketio.send_to_room({'type': f'stage-{stage}-visible', 'data': {'show': True}}, sid)


def add_chatroom(floor, code, title, sid):
    msocketio.send_to_room({'type': 'add-chat-room', 'data': {'floor': floor, 'room_code': code, 'title': title}}, sid)


def send_chat_history(room_code, client_sid):
    history = mroom.get_history(room_code)
    for chat_line in history:
        msg = {
            'type': 'chat-line',
            'data': chat_line
        }
        msocketio.send_to_room(msg, client_sid)


def send_time_when_to_show_stage(stage, user):
    settings = msettings.get_stage_settings()
    now = datetime.datetime.now()
    start_delay_at_start_timeslot = settings[f'stage-{stage}-start-timer-at'] == msettings.StageSetting.E_AFTER_START_TIMESLOT
    delay_start_timer_until_start_timeslot = settings[f'stage-{stage}-delay-start-timer-until-start-timeslot']
    delay = settings[f'stage-{stage}-delay']
    if start_delay_at_start_timeslot:
        show_time = user.timeslot + datetime.timedelta(seconds=delay)
    elif now > user.timeslot:
        show_time = now + datetime.timedelta(seconds=delay)
    elif delay_start_timer_until_start_timeslot:
        show_time = user.timeslot + datetime.timedelta(seconds=delay)
    else:
        show_time = now + datetime.timedelta(seconds=delay)
    log.info(f'user {user.full_name()} stage {stage}, show time at {show_time}')

    msocketio.send_to_room({'type': f'stage-show-time', 'data': {'stage': stage, 'show-time': str(show_time)}}, user.socketio_sid)


def stage_show_time_cb(msg, client_sid):
    stage = msg['data']['stage']
    show_stage(stage, client_sid)


msocketio.subscribe_on_type('new-end-user', new_end_user_cb)
msocketio.subscribe_on_type('stage-show-time', stage_show_time_cb)


add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_CLB, code='manuel-clb')
add_end_user('manuel-internaat', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_INTERNAAT, code='manuel-internaat')
add_end_user('gast1', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast1')
add_end_user('gast2', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast2')
add_end_user('gast3', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast3')
