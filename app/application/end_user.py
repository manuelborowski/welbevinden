from app.data.models import EndUser, Visit, Fair, Floor
from app.data import utils as mutils
import random, string, datetime
from app import log, db
from app.application import socketio as msocketio, room as mroom, settings as msettings


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


class Profile(EndUser.Profile):
    pass


class School(Fair.School):
    pass


class Level(Floor.Level):
    pass


def add_end_user(first_name, last_name, email, profile, sub_profile, timeslot=None, code=None):
    try:
        if not code:
            code = create_random_string(32)
        if not timeslot:
            timeslot = datetime.datetime.now().replace(microsecond=0)
        user = EndUser.query.filter(EndUser.email == email, EndUser.profile == profile, EndUser.sub_profile == sub_profile).first()
        if user:
            if profile != EndUser.Profile.E_GUEST:
                log.warning(f'Enduser {user.full_name()} {profile} already exists')
                return False
            visit = Visit.query.filter(Visit.end_user == user, Visit.timeslot == timeslot).first()
            if visit:
                log.warning(f'Enduser {user.full_name()} {profile} has already timeslot {timeslot}')
                return False
            visit = Visit(code=code, timeslot=timeslot)
            user.visits.append(visit)
            db.session.add(visit)
            db.session.commit()
            return user
        user = EndUser(first_name=first_name, last_name=last_name, email=email, profile=profile, sub_profile=sub_profile)
        visit = Visit(code=code, timeslot=timeslot)
        user.visits.append(visit)
        db.session.add(visit)
        db.session.add(user)
        db.session.commit()
        log.info(f'Enduser {user.full_name()} added')
        return user
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return None


def get_end_user(code, set_timestamp=False):
    try:
        user = EndUser.query.join(Visit).filter(Visit.code == code).first()
        if set_timestamp:
            user.last_login = datetime.datetime.now()
        return user
    except Exception as e:
        mutils.raise_error('could not find end user', e)
    return None


def get_visit(code, set_timestamp=False):
    try:
        visit = Visit.query.join(EndUser).filter(Visit.code == code).first()
        if set_timestamp:
            visit.end_user.last_login = datetime.datetime.now()
        return visit
    except Exception as e:
        mutils.raise_error('could not find visit', e)
    return None


def get_visit_by_socketio(socketio_sid):
    try:
        visit = Visit.query.filter(Visit.socketio_sid == socketio_sid).first()
        return visit
    except Exception as e:
        mutils.raise_error('could not find visit', e)
    return None


def set_socketio_sid(user_code, sid):
    try:
        visit = Visit.query.join(EndUser).filter(Visit.code == user_code).first()
        sid_valid = visit.socketio_sid is not None
        visit.socketio_sid = sid
        db.session.commit()
        visit.user_already_logged_in = sid_valid
        log.info(f'Enduser {visit.end_user.full_name()} logged in')
        return visit
    except Exception as e:
        mutils.raise_error(f'could not set socketio_sid {user_code} {sid}', e)


def remove_socketio_sid_cb(msg, sid):
    try:
        visit = Visit.query.join(EndUser).filter(Visit.socketio_sid == sid).first()
        if visit:
            visit.socketio_sid = None
            db.session.commit()
            log.info(f'Enduser {visit.end_user.full_name()} logged out')
        else:
            log.warning(f'Enduser with sid {sid} not found (enduser probably refreshed page)')
    except Exception as e:
        mutils.raise_error(f'could not remove socketio_sid {sid}', e)


msocketio.subscribe_on_type('disconnect', remove_socketio_sid_cb)


def new_end_user_cb(msg, client_sid):
    visit = set_socketio_sid(msg['data']['user_code'], client_sid)
    if visit.end_user.profile == Profile.E_FAIR_COWORKER:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
    elif visit.end_user.profile == Profile.E_GUEST:
        room = mroom.select_least_occupied_room(Level.E_CLB)
        room_owner = get_end_user(room.code)
        add_chatroom(Level.E_CLB, room.code, room_owner.full_name(), client_sid)
        send_chat_history(room.code, client_sid)
        send_time_when_to_show_stage(2, visit)
    else:
        show_stage(2, client_sid)
        show_stage(3, client_sid)
        add_chatroom(visit.end_user.profile, visit.code, visit.end_user.full_name(), client_sid)
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


def send_time_when_to_show_stage(stage, visit):
    settings = msettings.get_stage_settings()
    now = datetime.datetime.now()
    start_delay_at_start_timeslot = settings[f'stage-{stage}-start-timer-at'] == msettings.StageSetting.E_AFTER_START_TIMESLOT
    delay_start_timer_until_start_timeslot = settings[f'stage-{stage}-delay-start-timer-until-start-timeslot']
    delay = settings[f'stage-{stage}-delay']
    if start_delay_at_start_timeslot:
        show_time = visit.timeslot + datetime.timedelta(seconds=delay)
    elif now > visit.timeslot:
        show_time = now + datetime.timedelta(seconds=delay)
    elif delay_start_timer_until_start_timeslot:
        show_time = visit.timeslot + datetime.timedelta(seconds=delay)
    else:
        show_time = now + datetime.timedelta(seconds=delay)
    log.info(f'user {visit.end_user.full_name()} stage {stage}, show time at {show_time}')

    msocketio.send_to_room({'type': f'stage-show-time', 'data': {'stage': stage, 'show-time': str(show_time)}}, visit.socketio_sid)


def stage_show_time_cb(msg, client_sid):
    stage = msg['data']['stage']
    show_stage(stage, client_sid)


msocketio.subscribe_on_type('new-end-user', new_end_user_cb)
msocketio.subscribe_on_type('stage-show-time', stage_show_time_cb)


add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_FLOOR_COWORKER, Level.E_CLB, datetime.datetime(2021,1,1,14,0,0) ,'manuel-clb')
add_end_user('manuel-internaat', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_FLOOR_COWORKER, Level.E_INTERNAAT, datetime.datetime(2021,1,1,14,0,0), 'manuel-internaat')
add_end_user('gast1', 'testachternaam', 'gast1@gmail.com', Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 0, 0), 'gast1-1')
add_end_user('gast1', 'testachternaam', 'gast1@gmail.com', Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 30, 0), 'gast1-2')
add_end_user('gast1', 'testachternaam', 'gast1@gmail.com', Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 30, 0), 'gast1-3')
add_end_user('gast3', 'testachternaam', 'gast3@gmail.com', Profile.E_GUEST, None, datetime.datetime(2021, 1, 1, 14, 0, 0), 'gast3')
