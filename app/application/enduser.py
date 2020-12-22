from app.data.models import EndUser, Room, get_columns
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
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return True


def get_end_user(code, extract_columns=False):
    try:
        user = EndUser.query.filter(EndUser.code == code).first()
        if extract_columns:
            return get_columns(user)
        return user
    except Exception as e:
        mutils.raise_error('could not find end user', e)
    return None


def get_guests(room, extract_columns=False):
    try:
        guests = EndUser.query.filter(EndUser.room == room).all()
        if not extract_columns: return guests
        return [get_columns(g) for g in guests]
    except Exception as e:
        mutils.raise_error(f'could not get users in room {room}', e)
    return None



add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_CLB, code='manuel-clb')
add_end_user('testvoornaam', 'testachternaam', 'test@gmail.com', Profile.E_GAST, code='testvoornaam-gast')
