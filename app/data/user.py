from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import current_user
from app import db, log
import sys
from sqlalchemy_serializer import SerializerMixin

class User(UserMixin, db.Model, SerializerMixin):
    __tablename__ = 'users'

    class USER_TYPE:
        LOCAL = 'local'
        OAUTH = 'oauth'

    @staticmethod
    def get_zipped_types():
        return list(zip(['local', 'oauth'], ['LOCAL', 'OAUTH']))

    class LEVEL:
        GEBRUIKER = 1
        INSTELLEN = 2
        NAAM_LEERLING_ZIEN = 3
        ALLE_SCHOLEN_ZIEN = 4
        ADMIN = 5

        ls = ["GEBRUIKER", "INSTELLEN", "NAAM-LEERLING-ZIEN", "ALLE-SCHOLEN-ZIEN", "ADMINISTRATOR"]

        @staticmethod
        def i2s(i):
            return User.LEVEL.ls[i - 1]

    @staticmethod
    def get_zipped_levels():
        return list(zip(["1", "2", "3", "4", "5"], User.LEVEL.ls))

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    level = db.Column(db.Integer)
    user_type = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())

    @property
    def is_local(self):
        return self.user_type == User.USER_TYPE.LOCAL

    @property
    def is_oauth(self):
        return self.user_type == User.USER_TYPE.OAUTH

    ### level 1 ###
    @property
    def is_at_least_gebruiker(self):
        return self.level >= User.LEVEL.GEBRUIKER

    @property
    def is_strict_gebruiker(self):
        return self.level == User.LEVEL.GEBRUIKER

    ### level 2 ###
    @property
    def is_at_least_instellen(self):
        return self.level >= User.LEVEL.INSTELLEN

    ### level 3 ###
    @property
    def is_at_least_naam_leerling(self):
        return self.level >= User.LEVEL.NAAM_LEERLING_ZIEN

    @property
    def is_max_naam_leerling(self):
        return self.level <= User.LEVEL.NAAM_LEERLING_ZIEN

    ### level 4 ###
    @property
    def is_at_least_alle_scholen(self):
        return self.level >= User.LEVEL.ALLE_SCHOLEN_ZIEN

    @property
    def is_max_alle_scholen(self):
        return self.level <= User.LEVEL.ALLE_SCHOLEN_ZIEN

    ### level 5 ###
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
            return False

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def log(self):
        return '<User: {}/{}>'.format(self.id, self.username)

    def ret_dict(self):
        return {'id': self.id, 'DT_RowId': self.id, 'email': self.email, 'username': self.username,
                'level': User.LEVEL.i2s(self.level), 'user_type': self.user_type, 'last_login': self.last_login,
                'chbx': ''}


def add_user(data = {}):
    try:
        user = User()
        for k, v in data.items():
            if hasattr(user, k):
                if getattr(User, k).expression.type.python_type == type(v):
                    setattr(user, k, v.strip() if isinstance(v, str) else v)
        if 'password' in data:
            user.password = data['password']
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_user(user, data={}):
    try:
        for k, v in data.items():
            if hasattr(user, k):
                if getattr(User, k).expression.type.python_type == type(v):
                    setattr(user, k, v.strip() if isinstance(v, str) else v)
        if 'password' in data:
            user.password = data['password']
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def delete_users(ids=None):
    try:
        for id in ids:
            user = get_first_user({"id": id})
            db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_users(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = User.query
        for k, v in data.items():
            if hasattr(User, k):
                q = q.filter(getattr(User, k) == v)
        if order_by:
            q = q.order_by(getattr(User, order_by))
        if first:
            guest = q.first()
            return guest
        if count:
            return q.count()
        guests = q.all()
        return guests
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_user(data={}):
    try:
        user = get_users(data, first=True)
        return user
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


############ user overview list #########
def filter(query_in):
    #If the logged in user is NOT administrator, display the data of the current user only
    if not current_user.is_at_least_admin:
        return query_in.filter(User.id==current_user.id)
    return query_in


# Set up user_loader
# @login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


def pre_sql_query():
    return db.session.query(User)


def pre_sql_search(search_string):
    search_constraints = []
    search_constraints.append(User.username.like(search_string))
    search_constraints.append(User.email.like(search_string))
    return search_constraints


