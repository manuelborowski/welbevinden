from app import log, db
import json
from babel.dates import get_day_names, get_month_names
from app.data import settings as msettings


# woensdag 24 februari om 14 uur
def datetime_to_dutch_datetime_string(date, include_seconds=False):
    try:
        time_string = f"%H.%M{':%S' if include_seconds else ''}"
        date_string = f'{get_day_names(locale="nl")[date.weekday()]} {date.day} {get_month_names(locale="nl")[date.month]} om {date.strftime(time_string)}'
        return date_string
    except:
        return ''

#24/2/2022 22:12:23
def datetime_to_dutch_short(date, include_seconds=False, include_time=True):
    try:
        in_string = "%d/%m/%Y"
        if include_time:
            in_string = f"{in_string} %H.%M{':%S' if include_seconds else ''}"
        return date.strftime(in_string)
    except:
        return ''


class Warning(db.Model):
    __tablename__ = 'warnings'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime())
    message = db.Column(db.String(4096), default='')
    visible = db.Column(db.Boolean, default=True)

    def flat(self):
        return {
            'id': self.id,
            'visible': self.visible,
            'timestamp_dutch': datetime_to_dutch_datetime_string(self.timestamp),
            'message': self.message
        }

