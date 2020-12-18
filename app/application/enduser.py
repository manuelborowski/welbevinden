from app.data.models import EndUser
from app.data import utils as mutils
import random, string
from app import log, db

allowed_chars = string.ascii_letters + string.digits


def create_random_string(len):
    return ''.join(random.choice(allowed_chars) for i in range(len))


class Profile(EndUser.Profile):
    pass

def add_end_user(first_name, last_name, email, profile, timeslot=None):
    try:
        user = EndUser.query.filter(EndUser.first_name == first_name, EndUser.last_name == last_name,
                                    EndUser.email == email, EndUser.profile == profile).all()
        if user:
            log.warning(f'Enduser {first_name} {last_name} already exists')
            return False
        code = create_random_string(32)
        user = EndUser(first_name=first_name, last_name=last_name, email=email, profile=profile, code=code,
                       timeslot=timeslot)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return True

add_end_user('manuel', 'borowski', 'emmanuel.borowski@gmail.com', Profile.E_CLB)
add_end_user('testvoornaam', 'testachternaam', 'test@gmail.com', Profile.E_GAST)
