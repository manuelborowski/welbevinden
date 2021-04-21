from app.data.models import Guest, TimeslotConfiguration
from sqlalchemy import not_
from app.data import utils as mutils
from app import log, db
import datetime, random, string, sys


def add_guest_bulk(first_name, last_name, email, code):
    try:
        guest = Guest(first_name=first_name, last_name=last_name, email=email, code=code)
        db.session.add(guest)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_guest_commit():
    try:
        db.session.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_guest(first_name, last_name, email, code):
    try:
        add_guest_bulk(first_name, last_name, email, code)
        add_guest_commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_guests(email=None, code=None, first=False):
    try:
        guests = Guest.query
        if email:
            guests = guests.filter(Guest.email == email)
        if code:
            guests = guests.filter(Guest.code == code)
        if first:
            guest = guests.first()
            return guest
        guests = guests.all()
        return guests()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_guest(email=None, code=None):
    try:
        guest = get_guests(email=email, code=code, first=True)
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_invite():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.invite_email_sent)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_ack():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.ack_email_sent)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def pre_filter():
    return db.session.query(Guest)


def search_data(search_string):
    search_constraints = []
    # search_constraints.append(SchoolReservation.name_school.like(search_string))
    # search_constraints.append(SchoolReservation.name_teacher_1.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out


