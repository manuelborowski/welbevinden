from app.data.models import AvailablePeriod, SchoolReservation, TeamsMeeting
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


def get_available_period_by_id(id=None):
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


def add_registration(data):
    try:
        meetings = []
        for md in data['teams-meetings']:
            try:
                if md['meeting-email'] == '': continue
                date = datetime.datetime.strptime(':'.join(md['meeting-date'].split(':')[:2]), '%Y-%m-%dT%H:%M')
                meeting = TeamsMeeting(classgroup=md['classgroup'], date=date, email=md['meeting-email'])
                db.session.add(meeting)
                meetings.append(meeting)
            except:
                continue

        period = AvailablePeriod.query.get(data['period_id'])
        reservation = SchoolReservation(name_school=data['name-school'], name_teacher_1=data['name-teacher-1'],
                                        name_teacher_2=data['name-teacher-2'], name_teacher_3=data['name-teacher-3'], email=data['email'],
                                        phone=data['phone'],
                                        address=data['address'], postal_code=data['postal-code'],
                                        city=data['city'], nbr_students=data['number-students'], period=period,
                                        reservation_nbr_boxes=data['nbr_boxes'], meetings=meetings,
                                        reservation_code=data['reservation-code'])
        db.session.add(reservation)
        db.session.commit()
        log.info(f'reservation added {data["reservation-code"]}')
        return reservation
    except Exception as e:
        mutils.raise_error(f'could not add registration {data["name-school"]}', e)
    return None


def update_registration_by_code(data):
    # name_school, name_teacher_1, name_teacher_2, name_teacher_3, email, phone, address,
    #                             postal_code, city,
    #                             nbr_students, available_period_id, nbr_boxes, meeting_email, meeting_date, code):
    try:
        # period = AvailablePeriod.query.get(data['reservation-code'])
        reservation = SchoolReservation.query.join(TeamsMeeting, AvailablePeriod).filter(SchoolReservation.reservation_code == data['reservation-code']).first()

        meetings_cache = {m.classgroup + m.email + str(m.date): m for m in reservation.meetings}
        # for meeting in reservation.meetings:
        #     meetings_cache[meeting.classgroup + meeting.email + str(meeting.date)] = meeting

        meetings = []
        new_meetings = []
        for md in data['teams-meetings']:
            try:
                if md['meeting-email'] == '': continue
                date = datetime.datetime.strptime(':'.join(md['meeting-date'].split(':')[:2]), '%Y-%m-%dT%H:%M')
                key = md['classgroup'] + md['meeting-email'] + str(date)
                if key in meetings_cache:
                    new_meetings.append(meetings_cache[key])
                    del meetings_cache[key]
                    continue
                meeting = TeamsMeeting(classgroup=md['classgroup'], date=date, email=md['meeting-email'])
                db.session.add(meeting)
                new_meetings.append(meeting)
            except:
                continue
        reservation.meetings = new_meetings
        for k, v in meetings_cache.items():
            db.session.delete(v)

        # reservation.name_school = name_school
        # reservation.name_teacher_1 = name_teacher_1
        # reservation.name_teacher_2 = name_teacher_2
        # reservation.name_teacher_3 = name_teacher_3
        # reservation.email = email
        # reservation.phone = phone
        # reservation.address = address
        # reservation.postal_code = postal_code
        # reservation.city = city
        # reservation.nbr_students = nbr_students
        # reservation.period = period
        # reservation.reservation_nbr_boxes = nbr_boxes
        # reservation.meeting_email = meeting_email
        # reservation.meeting_date = meeting_date
        # reservation.ack_email_sent = False
        # db.session.commit()
        # log.info(f'reservation update {code}')
        return True
    except Exception as e:
        pass
        # mutils.raise_error(f'could not update registration {code}', e)
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


def add_meeting(classgroup, date, email):
    try:
        meeting = TeamsMeeting(classgroup=classgroup, date=date, email=email)
        db.session.add(meeting)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not add teams meeting', e)
    return None


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


