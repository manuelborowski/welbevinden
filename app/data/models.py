from app import log, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
import datetime
from babel.dates import get_day_names, get_month_names


# woensdag 24 februari om 14 uur
def datetime_to_dutch_datetime_string(date):
    try:
        date_string = f'{get_day_names(locale="nl")[date.weekday()]} {date.day} {get_month_names(locale="nl")[date.month]} om {date.strftime("%H.%M")}'
        return date_string
    except:
        return ''


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    class USER_TYPE:
        LOCAL = 'local'
        OAUTH = 'oauth'

    @staticmethod
    def get_zipped_types():
        return list(zip(['local', 'oauth'], ['LOCAL', 'OAUTH']))

    class LEVEL:
        USER = 1
        SUPERVISOR = 3
        ADMIN = 5

        ls = ["GEBRUIKER", "SECRETARIAAT", "ADMINISTRATOR"]

        @staticmethod
        def i2s(i):
            if i == 1:
                return User.LEVEL.ls[0]
            elif i == 3:
                return User.LEVEL.ls[1]
            if i == 5:
                return User.LEVEL.ls[2]

    @staticmethod
    def get_zipped_levels():
        return list(zip(["1", "3", "5"], User.LEVEL.ls))

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    level = db.Column(db.Integer)
    user_type = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    settings = db.relationship('Settings', cascade='all, delete', backref='user', lazy='dynamic')

    @property
    def is_local(self):
        return self.user_type == User.USER_TYPE.LOCAL

    @property
    def is_oauth(self):
        return self.user_type == User.USER_TYPE.OAUTH

    @property
    def is_at_least_user(self):
        return self.level >= User.LEVEL.USER

    @property
    def is_strict_user(self):
        return self.level == User.LEVEL.USER

    @property
    def is_at_least_supervisor(self):
        return self.level >= User.LEVEL.SUPERVISOR

    @property
    def is_at_least_admin(self):
        return self.level >= User.LEVEL.ADMIN

    @property
    def password(self):
        raise AttributeError('Paswoord kan je niet lezen.')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return True

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def log(self):
        return '<User: {}/{}>'.format(self.id, self.username)

    def ret_dict(self):
        return {'id': self.id, 'DT_RowId': self.id, 'email': self.email, 'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'level': User.LEVEL.i2s(self.level), 'user_type': self.user_type, 'last_login': self.last_login,
                'chbx': ''}


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(db.Text)
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)


class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    phone = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    invite_email_sent = db.Column(db.Boolean, default=True)
    ack_email_sent = db.Column(db.Boolean, default=True)
    email_send_retry = db.Column(db.Integer(), default=0)
    enabled = db.Column(db.Boolean, default=True)
    code = db.Column(db.String(256), default='')
    timeslot = db.Column(db.DateTime())

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'{self.email}/{self.full_name()}/{self.visits[0].code}/{self.profile}'

    def flat(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'email': self.email,
            'first-name': self.first_name,
            'last-name': self.last_name,
            'full_name': f'{self.first_name} {self.last_name}',
            'last_login': self.last_login,
            'reservation-code': self.code,
            'invite_email_sent': self.invite_email_sent,
            'ack_email_sent': self.ack_email_sent,
            'email-send-retry': self.email_send_retry,
            'enabled': self.enabled,
            'timeslot': datetime_to_dutch_datetime_string(self.timeslot),
        }

    ack_email_sent_cb = []

    def set_ack_email_sent(self, value):
        self.ack_email_sent = value
        db.session.commit()
        for cb in Guest.ack_email_sent_cb:
            cb[0](value, cb[1])
        return True

    @staticmethod
    def subscribe_ack_email_sent(cb, opaque):
        Guest.ack_email_sent_cb.append((cb, opaque))
        return True

    invite_email_sent_cb = []

    def set_invite_email_sent(self, value):
        self.invite_email_sent = value
        db.session.commit()
        for cb in Guest.invite_email_sent_cb:
            cb[0](value, cb[1])
        return True

    @staticmethod
    def subscribe_invite_email_sent(cb, opaque):
        Guest.invite_email_sent_cb.append((cb, opaque))
        return True

    email_send_retry_cb = []

    def set_email_send_retry(self, value):
        self.email_send_retry = value
        db.session.commit()
        for cb in Guest.email_send_retry_cb:
            cb[0](value, cb[1])
        return True

    @staticmethod
    def subscribe_email_send_retry(cb, opaque):
        Guest.email_send_retry_cb.append((cb, opaque))
        return True

    enabled_cb = []

    def set_enabled(self, value):
        self.enabled = value
        db.session.commit()
        for cb in Guest.enabled_cb:
            cb[0](value, cb[1])
        return True

    @staticmethod
    def subscribe_enabled(cb, opaque):
        Guest.enabled_cb.append((cb, opaque))
        return True


class TimeslotConfiguration(db.Model):
    __tablename__ = 'timeslot_configurations'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    length = db.Column(db.Integer, default=15)  # in minutes
    nbr_of_timeslots = db.Column(db.Integer, default=20)
    items_per_timeslot = db.Column(db.Integer, default=8)
    active = db.Column(db.Boolean, default=True)

    def period_string(self):
        start_date = self.date.strftime('%d/%m/%Y')
        end_date = (self.date + datetime.timedelta(days=self.length - 1)).strftime('%d/%m/%Y')
        return f'{start_date} tem {end_date}'
