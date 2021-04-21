from app.data import utils as mutils, guest as mguest
import random, string, datetime
from app import log, db
import sys
from app.application import socketio as msocketio


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def add_guest(first_name, last_name, email, code=None):
    try:
        guest = mguest.get_first_guest(email=email)
        if guest:
            return guest
        if not code:
            code = create_random_string(32)
        guest = mguest.add_guest(first_name, last_name, email, code)
        log.info(f'{sys._getframe().f_code.co_name}: {email}')
        return guest
    except Exception as e:
        mutils.raise_error(f'{sys._getframe().f_code.co_name}:', e)
    return None


add_guest('manuel', 'borowski', 'emmanuel.borowski@gmail.com')
