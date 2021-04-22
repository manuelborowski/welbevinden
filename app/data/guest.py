from app.data.models import Guest
from sqlalchemy import not_
from app import log, db
import sys


def add_guest_bulk(full_name=None, first_name=None, last_name=None, phone=None, email=None, code=None):
    try:
        guest = Guest(full_name=full_name, first_name=first_name, last_name=last_name, phone=phone, email=email, code=code)
        db.session.add(guest)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_guest_commit():
    try:
        db.session.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_guest(full_name=None, first_name=None, last_name=None, phone=None, email=None, code=None):
    try:
        add_guest_bulk(full_name=full_name, first_name=first_name, last_name=last_name, phone=phone, email=email, code=code)
        add_guest_commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_guests(id=None, email=None, code=None, timeslot=None, enabled=None, first=False, count=False):
    try:
        guests = Guest.query
        if id:
            guests = guests.filter(Guest.id == id)
        if email:
            guests = guests.filter(Guest.email == email)
        if code:
            guests = guests.filter(Guest.code == code)
        if timeslot:
            guests = guests.filter(Guest.timeslot == timeslot)
        if enabled is not None:
            guests = guests.filter(Guest.enabled == enabled)
        if first:
            guest = guests.first()
            return guest
        if count:
            return guests.count()
        guests = guests.all()
        return guests
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_guest(id=None, email=None, code=None):
    try:
        guest = get_guests(id=id, email=email, code=code, first=True)
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_guest_count(timeslot=None):
    try:
        count = get_guests(timeslot=timeslot, count=True)
        return count
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return -1


def update_guest(guest, full_name=None, first_name=None, last_name=None, phone=None, timeslot=None):
    try:
        if full_name:
            guest.full_name = full_name
        if first_name:
            guest.first_name = first_name
        if last_name:
            guest.last_name = last_name
        if phone:
            guest.phone = phone
        if timeslot:
            guest.timeslot = timeslot
        db.session.commit()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_timeslot(guest, timeslot):
    try:
        guest.timeslot = timeslot
        db.session.commit()
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


def subscribe_ack_email_sent(cb, opaque):
    return Guest.subscribe_ack_email_sent(cb, opaque)


def subscribe_invite_email_sent(cb, opaque):
    return Guest.subscribe_invite_email_sent(cb, opaque)


def subscribe_email_send_retry(cb, opaque):
    return Guest.subscribe_email_send_retry(cb, opaque)


def subscribe_enabled(cb, opaque):
    return Guest.subscribe_enabled(cb, opaque)


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
        em = i.flat()
        em.update({
            'row_action': f"{i.id}",
            'id': i.id,
            'DT_RowId': i.id
        })
        out.append(em)
    return out


