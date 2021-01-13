from app.data.models import AvailablePeriod, SchoolReservation
from app.data import utils as mutils
from app import db, log
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
    available_periods = []
    try:
        periods = AvailablePeriod.query.filter(AvailablePeriod.active == True).order_by(AvailablePeriod.date).all()
        for period in periods:
            reservation_count = SchoolReservation.query.filter(SchoolReservation.period == period).count()
            start_date = period.date.strftime('%d/%m/%Y')
            end_date = (period.date + datetime.timedelta(days=period.length - 1)).strftime('%d/%m/%Y')
            available_periods.append({
                'id': period.id,
                'period': f'{start_date} tem {end_date}',
                'length': period.length,
                'max_number': period.max_nbr_boxes,
                'current_number': reservation_count,
                'boxes_left': period.max_nbr_boxes - reservation_count,
            })
        return available_periods
    except Exception as e:
        mutils.raise_error('could not get available periods', e)
    return []


def create_random_string(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def add_registration(name_school, name_teacher_1, name_teacher_2, name_teacher_3, phone, address, postal_code, city,
                     nbr_students, available_period_id, nbr_boxes, meeting_email, meeting_date):
    try:
        code = create_random_string(32)
        period = AvailablePeriod.query.get(available_period_id)
        date = datetime.datetime.strptime(meeting_date.split('+')[0], '%Y-%m-%dT%H:%M:%S')
        reservation = SchoolReservation(name_school=name_school, name_teacher_1=name_teacher_1,
                                        name_teacher_2=name_teacher_2, name_teacher_3=name_teacher_3, phone=phone,
                                        address=address, postal_code=postal_code,
                                        city=city, nbr_students=nbr_students, period=period,
                                        reservation_nbr_boxes=nbr_boxes, meeting_email=meeting_email, meeting_date=date,
                                        reservation_code=code)
        db.session.add(reservation)
        db.session.commit()
        log.info(f'reservation added {code}')
        return True
    except Exception as e:
        mutils.raise_error(f'could not add registration {name_school}', e)
    return False


add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)
