import sys
from app import log, db
from sqlalchemy import text
from sqlalchemy_serializer import SerializerMixin


class StudentCare(db.Model, SerializerMixin):
    __tablename__ = 'student_cares'

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
        student = StudentCare()
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(StudentCare, k).expression.type.python_type == type(v):
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
                if getattr(StudentCare, k).expression.type.python_type == type(v):
                    setattr(student, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def delete_students(ids=None):
    try:
        for id in ids:
            student = get_first_student({"id": id})
            db.session.delete(student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_students(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = StudentCare.query
        for k, v in data.items():
            if hasattr(StudentCare, k):
                q = q.filter(getattr(StudentCare, k) == v)
        if order_by:
            q = q.order_by(getattr(StudentCare, order_by))
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
        user = get_students(data, first=True)
        return user
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None



############ student overview list #########
def pre_filter():
    return db.session.query(StudentCare)


def filter_data(query, filter):
    if filter and 'type' in filter[0] and filter[0]['type'] == 'checkbox':
        for cb in filter[0]['value']:
            query = query.filter(text(cb['id']), cb['checked'])
    for f in filter:
        if f['type'] == 'select' and f['value'] != 'none':
            query = query.filter(getattr(StudentCare, f['name']) == (f['value'] == 'True'))
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(StudentCare.s_first_name.like(search_string))
    search_constraints.append(StudentCare.s_last_name.like(search_string))
    return search_constraints

