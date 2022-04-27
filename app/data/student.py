import sys
from app import log, db
from sqlalchemy_serializer import SerializerMixin


class Student(db.Model, SerializerMixin):
    __tablename__ = 'students'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer, primary_key=True)
    #student
    s_first_name = db.Column(db.String(256), default='')
    s_last_name = db.Column(db.String(256), default='')
    s_code = db.Column(db.String(256), default='')
    s_date_of_birth = db.Column(db.Date())
    s_sex = db.Column(db.String(256), default='')
    #intaker
    i_first_name = db.Column(db.String(256), default='')
    i_last_name = db.Column(db.String(256), default='')
    i_code = db.Column(db.String(256), default='')
    i_intake_date = db.Column(db.DateTime())
    #contactgegevens
    vorige_school = db.Column(db.Text, default='')
    vorig_clb = db.Column(db.Text, default='')
    #inschrijving
    f_gemotiveerd_verslag = db.Column(db.Boolean, default=False)
    f_verslag_ontbindende_voorwaarden = db.Column(db.Boolean, default=False)
    f_geen_verslag_specifieke_behoefte = db.Column(db.Boolean, default=False)
    #nood aan voorspelbaarheid
    f_nood_aan_voorspelbaarheid = db.Column(db.Boolean, default=False)
    #thuissituatie
    thuissituatie = db.Column(db.Text, default='')
    #schoolverloop
    schoolloopbaan = db.Column(db.Text, default='')
    advies_school = db.Column(db.Text, default='')
    definitieve_studiekeuze = db.Column(db.Text, default='')
    #psychomedische info en verstandelijke mogelijkheden
    f_ass = db.Column(db.Boolean, default=False)
    ass = db.Column(db.Text, default='')
    f_add = db.Column(db.Boolean, default=False)
    add = db.Column(db.Text, default='')
    f_adhd = db.Column(db.Boolean, default=False)
    adhd = db.Column(db.Text, default='')
    f_dcd = db.Column(db.Boolean, default=False)
    dcd = db.Column(db.Text, default='')
    f_hoogbegaafd = db.Column(db.Boolean, default=False)
    hoogbegaafd = db.Column(db.Text, default='')
    f_dyscalculie = db.Column(db.Boolean, default=False)
    dyscalculie = db.Column(db.Text, default='')
    f_dyslexie = db.Column(db.Boolean, default=False)
    dyslexie = db.Column(db.Text, default='')
    f_dysorthografie = db.Column(db.Boolean, default=False)
    dysorthografie = db.Column(db.Text, default='')
    f_stos_dysfasie = db.Column(db.Boolean, default=False)
    stos_dysfasie = db.Column(db.Text, default='')
    f_andere = db.Column(db.Boolean, default=False)
    andere = db.Column(db.Text, default='')
    motoriek = db.Column(db.Text, default='')
    gezondheid = db.Column(db.Text, default='')
    #sociaal emotioneel functioneren
    groepsfunctioneren = db.Column(db.Text, default='')
    individueel_functioneren = db.Column(db.Text, default='')
    communicatie = db.Column(db.Text, default='')
    #leerontwikkeling
    algemeen = db.Column(db.Text, default='')
    taalvaardigheid = db.Column(db.Text, default='')
    rekenvaardigheid = db.Column(db.Text, default='')
    #ondersteuning
    ondersteunende_maatregelen = db.Column(db.Text, default='')
    schoolexterne_zorg = db.Column(db.Text, default='')


def add_student(data = {}):
    try:
        student = Student()
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(Student, k).expression.type.python_type == type(v):
                    setattr(student, k, v.strip() if isinstance(v, str) else v)
        db.session.add(student)
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_student(student, data={}):
    try:
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(Student, k).expression.type.python_type == type(v):
                    setattr(student, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_students(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = Student.query
        for k, v in data.items():
            if hasattr(Student, k):
                q = q.filter(getattr(Student, k) == v)
        if order_by:
            q = q.order_by(getattr(Student, order_by))
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


def get_first_student(data={}):
    try:
        guest = get_students(data, first=True)
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None



############ student overview list #########
def pre_filter():
    return db.session.query(Student)


def filter_data(query, filter):
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Student.s_first_name.like(search_string))
    search_constraints.append(Student.s_last_name.like(search_string))
    return search_constraints

