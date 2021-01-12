from app.data.models import AvailablePeriod, SchoolReservation
from app.data import utils as mutils
from app import db, log
import datetime

def add_available_period(date, length, max_reservations):
    try:
        period = AvailablePeriod.query.filter(AvailablePeriod.date == date, AvailablePeriod.active == True).first()
        if period:
            log.warning(f'AvailablePeriod {date} already exists')
            return None
        period = AvailablePeriod(date=date, length=length, max_reservations=max_reservations)
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
            reservation_count = SchoolReservation.query.filter(SchoolReservation.reservation_date == period.date).count()
            start_date = period.date.strftime('%d/%m/%Y')
            end_date = (period.date + datetime.timedelta(days=period.length - 1)).strftime('%d/%m/%Y')
            available_periods.append({
                'id': period.id,
                'period': f'{start_date} tem {end_date}',
                'length': period.length,
                'max_number': period.max_reservations,
                'current_number': reservation_count,
                'boxes_left': period.max_reservations - reservation_count,
            })
        return available_periods
    except Exception as e:
        mutils.raise_error('could not get available periods', e)
    return []


add_available_period(datetime.datetime(year=2021, month=1, day=25), 4, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=1), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=8), 5, 4)
add_available_period(datetime.datetime(year=2021, month=2, day=22), 5, 4)
add_available_period(datetime.datetime(year=2021, month=3, day=1), 5, 4)