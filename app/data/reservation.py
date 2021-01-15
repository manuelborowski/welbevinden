from app.data.models import AvailablePeriod, SchoolReservation
from app.data import utils as mutils
from app import log, db
import datetime, random, string


def add_available_period(date, length, max_nbr_boxes):
    try:
        period = AvailablePeriod.query.filter(AvailablePeriod.date == date, AvailablePeriod.active == True).first()
        if period:
            log.warning(f'AvailablePeriod {date} already exists')
            return None
        period = AvailablePeriod(date=date, length=length, max_nbr_boxes=max_nbr_boxes)
        db.session.add(period)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not add available period', e)
    return None


def get_available_periods():
    try:
        periods = AvailablePeriod.query.filter(AvailablePeriod.active == True).order_by(AvailablePeriod.date).all()
        return periods
    except Exception as e:
        mutils.raise_error('could not get available periods', e)
    return []


def get_available_period(id=None):
    period = None
    try:
        if id:
            period = AvailablePeriod.query.get(id)
        return period
    except Exception as e:
        mutils.raise_error('could not get period', e)
    return None


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def add_registration(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone, address, postal_code,
                     city,
                     nbr_students, available_period_id, nbr_boxes, meeting_email, meeting_date, code):
    try:
        period = AvailablePeriod.query.get(available_period_id)
        reservation = SchoolReservation(name_school=name_school, name_teacher_1=name_teacher_1,
                                        name_teacher_2=name_teacher_2, name_teacher_3=name_teacher_3, email=email,
                                        phone=phone,
                                        address=address, postal_code=postal_code,
                                        city=city, nbr_students=nbr_students, period=period,
                                        reservation_nbr_boxes=nbr_boxes, meeting_email=meeting_email,
                                        meeting_date=meeting_date,
                                        reservation_code=code)
        db.session.add(reservation)
        db.session.commit()
        log.info(f'reservation added {code}')
        return True
    except Exception as e:
        mutils.raise_error(f'could not add registration {name_school}', e)
    return False


def update_registration_by_code(name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone, address,
                                postal_code, city,
                                nbr_students, available_period_id, nbr_boxes, meeting_email, meeting_date, code):
    try:
        period = AvailablePeriod.query.get(available_period_id)
        reservation = SchoolReservation.query.filter(SchoolReservation.reservation_code == code).first()
        reservation.name_school = name_school
        reservation.name_teacher_1 = name_teacher_1
        reservation.name_teacher_2 = name_teacher_2
        reservation.name_teacher_3 = name_teacher_3
        reservation.email = email
        reservation.phone = phone
        reservation.address = address
        reservation.postal_code = postal_code
        reservation.city = city
        reservation.nbr_students = nbr_students
        reservation.period = period
        reservation.reservation_nbr_boxes = nbr_boxes
        reservation.meeting_email = meeting_email
        reservation.meeting_date = meeting_date
        reservation.ack_email_sent = False
        db.session.commit()
        log.info(f'reservation update {code}')
        return True
    except Exception as e:
        mutils.raise_error(f'could not update registration {code}', e)
    return False


def get_registration_by_code(code):
    reservation = SchoolReservation.query.filter(SchoolReservation.active, SchoolReservation.enabled)
    reservation = reservation.filter(SchoolReservation.reservation_code == code)
    reservation = reservation.first()
    return reservation


def get_registration_by_id(id):
    reservation = SchoolReservation.query.filter(SchoolReservation.id == id)
    reservation = reservation.first()
    return reservation


def get_first_not_sent_registration():
    reservation = SchoolReservation.query.filter(SchoolReservation.active, SchoolReservation.enabled)
    reservation = reservation.filter(SchoolReservation.ack_email_sent == False)
    reservation = reservation.first()
    return reservation


def update_registration(registration, nbr_boxes=None):
    if nbr_boxes is not None:
        registration.reservation_nbr_boxes = nbr_boxes
    db.session.commit()


def pre_filter():
    return db.session.query(SchoolReservation).join(AvailablePeriod)


def search_data(search_string):
    search_constraints = []
    search_constraints.append(SchoolReservation.name_school.like(search_string))
    search_constraints.append(SchoolReservation.name_teacher_1.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out

