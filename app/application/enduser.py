from app.data.models import EndUser
from app.data import utils as mutils
import random, string, datetime
from app import log, db
from app.application import socketio as msocketio, room as mroom

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


def set_socketio_sid(user_code, sid):
    try:
        user = EndUser.query.filter(EndUser.code == user_code).first()
        user.socketio_sid = sid
        db.session.commit()
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
        pass
    elif user.profile == EndUser.Profile.E_GAST:
        room = mroom.select_least_occupied_room(EndUser.Profile.E_CLB)
        room_owner = get_end_user(room.code)
        msocketio.send_to_room({'type' : 'add-chat-room', 'data' : {'floor': EndUser.Profile.E_CLB, 'room_code' : room.code, 'title' : room_owner.full_name()}}, client_sid)
        # transmit all current messages to the client
        history = mroom.get_history(room.code)
        for chat_line in history:
            msg = {
                'type': 'chat-line',
                'data': chat_line
            }
            msocketio.send_to_room(msg, client_sid)
    else:
        # create a room at the client side
        msocketio.send_to_room({'type' : 'add-chat-room', 'data' : {'floor': user.profile, 'room_code' : user.code, 'title' : user.full_name()}}, client_sid)
        # transmit all current messages to the client
        history = mroom.get_history(msg['data']['user_code'])
        for chat_line in history:
            msg = {
                'type': 'chat-line',
                'data' : chat_line
            }
            msocketio.send_to_room(msg, client_sid)


msocketio.subscribe_on_type('new-end-user', new_end_user_cb)

add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_CLB, code='manuel-clb')
add_end_user('manuel-internaat', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_INTERNAAT, code='manuel-internaat')
add_end_user('gast1', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast1')
add_end_user('gast2', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast2')
add_end_user('gast3', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='gast3')
