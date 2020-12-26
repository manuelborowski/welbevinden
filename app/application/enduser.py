from app.data.models import EndUser
from app.data import utils as mutils
import random, string
from app import log, db

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


def get_end_user(code):
    try:
        user = EndUser.query.filter(EndUser.code == code).first()
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
    except Exception as e:
        mutils.raise_error(f'could not set socketio_sid {user_code} {sid}', e)


def remove_socketio_sid(sid):
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


add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_CLB, code='manuel-clb')
add_end_user('manuel-internaat', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_INTERNAAT, code='manuel-internaat')
add_end_user('testvoornaam', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='testvoornaam-gast')
