import sys
from app import log, db
from sqlalchemy import text
from sqlalchemy_serializer import SerializerMixin

class School(db.Model, SerializerMixin):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    jaar = db.Column(db.String(256), default='')
    adres = db.Column(db.String(256), default='')
    studierichting = db.Column(db.String(256), default='')
    attest = db.Column(db.String(256), default='')
    student_id = db.Column(db.Integer, db.ForeignKey('student_intakes.id'), nullable=False)


class StudenIntake(db.Model, SerializerMixin):
    __tablename__ = 'student_intakes'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'
    serialize_rules = ('-school_lijst.student',)

    id = db.Column(db.Integer, primary_key=True)
    #student
    s_first_name = db.Column(db.String(256), default='')
    s_last_name = db.Column(db.String(256), default='')
    s_code = db.Column(db.String(256), default='')
    s_date_of_birth = db.Column(db.Date())
    s_sex = db.Column(db.String(256), default='')
    s_officieel_adres_bij = db.Column(db.String(256), default='')
    s_officieel_adres_andere = db.Column(db.String(256), default='')

    s_roepnaam = db.Column(db.String(256), default='')
    s_geboorteplaats = db.Column(db.String(256), default='')
    s_geboorteland = db.Column(db.String(256), default='')
    s_nationaliteit = db.Column(db.String(256), default='')
    s_rijksregister = db.Column(db.String(256), default='')
    s_adres = db.Column(db.String(256), default='')
    s_postnummer = db.Column(db.Integer, default=0)
    s_gemeente = db.Column(db.String(256), default='')
    s_gsm = db.Column(db.String(256), default='')
    s_mail = db.Column(db.String(256), default='')

    #intaker
    i_first_name = db.Column(db.String(256), default='')
    i_last_name = db.Column(db.String(256), default='')
    i_code = db.Column(db.String(256), default='')
    i_intake_date = db.Column(db.DateTime())



    studierichting = db.Column(db.String(256), default='')
    clil_keuze = db.Column(db.String(256), default='')

    #schoolloopbaan
    school_type = db.Column(db.String(256), default='')
    school_naam = db.Column(db.String(256), default='')
    school_blo_type = db.Column(db.String(256), default='')
    school_adres = db.Column(db.String(256), default='')
    school_voorlopig_advies = db.Column(db.String(256), default='')
    school_lijst = db.relationship('School', backref='student', lazy=True, cascade="all, delete-orphan")

    school_extra_info = db.Column(db.String(256), default='')

    #aandachtspunten voor de school
    f_contact = db.Column(db.Boolean, default=False)
    extra_begeleiding = db.Column(db.Text, default='')
    f_extra_begeleiding = db.Column(db.Boolean, default=False)
    extra_begeleiding_welke = db.Column(db.Text, default='')
    extra_begeleiding_door_wie = db.Column(db.Text, default='')

    f_ondersteuningsnetwerk = db.Column(db.Boolean, default=False)
    zorg_id = db.Column(db.Integer, default=None)

    specifieke_onderwijsbehoeften = db.Column(db.String(256), default='')

    andere_schoolproblemen = db.Column(db.Text, default='')

    samen_met_leerling1 = db.Column(db.String(256), default='')
    samen_met_leerling2 = db.Column(db.String(256), default='')

    betaling_email = db.Column(db.String(256), default='')
    betaling_wijze = db.Column(db.String(256), default='')
    domiciliering_iban = db.Column(db.String(256), default='')
    domiciliering_bic = db.Column(db.String(256), default='')
    domiciliering_rekeninghouder = db.Column(db.String(256), default='')
    
    #gezin
    g_spreektaal = db.Column(db.String(256), default='')
    g_aantal_kinderen = db.Column(db.Integer, default=1)
    g_achternaam_ouder_1 = db.Column(db.String(256), default='')
    g_voornaam_ouder_1 = db.Column(db.String(256), default='')
    g_relatie_ouder_1 = db.Column(db.String(256), default='')
    g_beroep_ouder_1 = db.Column(db.String(256), default='')
    g_gsm_ouder_1 = db.Column(db.String(256), default='')
    g_email_ouder_1 = db.Column(db.String(256), default='')
    f_verschillend_adres_ouder_1 = db.Column(db.Boolean, default=False)
    g_adres_ouder_1 = db.Column(db.String(256), default='')
    g_postnummer_ouder_1 = db.Column(db.Integer, default=0)
    g_gemeente_ouder_1 = db.Column(db.String(256), default='')

    g_achternaam_ouder_2 = db.Column(db.String(256), default='')
    g_voornaam_ouder_2 = db.Column(db.String(256), default='')
    g_relatie_ouder_2 = db.Column(db.String(256), default='')
    g_beroep_ouder_2 = db.Column(db.String(256), default='')
    g_gsm_ouder_2 = db.Column(db.String(256), default='')
    g_email_ouder_2 = db.Column(db.String(256), default='')
    f_verschillend_adres_ouder_2 = db.Column(db.Boolean, default=False)
    g_adres_ouder_2 = db.Column(db.String(256), default='')
    g_postnummer_ouder_2 = db.Column(db.Integer, default=0)
    g_gemeente_ouder_2 = db.Column(db.String(256), default='')

    g_vaste_telefoon = db.Column(db.String(256), default='')
    g_vaste_telefoon_bij = db.Column(db.String(256), default='')
    g_noodnummer = db.Column(db.String(256), default='')
    g_noodnummer_bij = db.Column(db.String(256), default='')

    #Motivatie
    m_waarom_onze_school = db.Column(db.Text, default='')
    m_waarom_deze_richting = db.Column(db.Text, default='')

    #Vrije tijd
    v_hobby = db.Column(db.Text, default='')

    #zwembrevet
    f_zwembrevet = db.Column(db.Boolean, default=True)

    #Gezondheid
    g_problemen = db.Column(db.Text, default='')
    g_medicatie = db.Column(db.Text, default='')
    g_huisarts_naam = db.Column(db.String(256), default='')
    g_huisarts_adres = db.Column(db.String(256), default='')
    g_huisarts_telefoon = db.Column(db.String(256), default='')

    #Toestemming
    f_klasfoto = db.Column(db.Boolean, default=True)
    f_schoolgids = db.Column(db.Boolean, default=True)
    f_website = db.Column(db.Boolean, default=True)
    f_nieuwsbrief = db.Column(db.Boolean, default=True)
    f_evenementen = db.Column(db.Boolean, default=True)
    f_sociale_media = db.Column(db.Boolean, default=True)
    f_peilingen = db.Column(db.Boolean, default=True)
    f_baso_onderwijs = db.Column(db.Boolean, default=True)
    f_baso_resultaten = db.Column(db.Boolean, default=True)
    f_baso_werkhouding = db.Column(db.Boolean, default=True)
    f_baso_leefhouding = db.Column(db.Boolean, default=True)
    f_baso_noden = db.Column(db.Boolean, default=True)
    f_baso_advies = db.Column(db.Boolean, default=True)
    f_dossier_attest = db.Column(db.Boolean, default=True)
    f_dossier_verslag = db.Column(db.Boolean, default=True)
    f_clb = db.Column(db.Boolean, default=True)
    f_ouderleerlingen_adres = db.Column(db.Boolean, default=True)
    f_ouderleerlingen_telefoon = db.Column(db.Boolean, default=True)
    f_ouderleerlingen_gsm = db.Column(db.Boolean, default=True)
    f_ouderleerlingen_geboortedatum = db.Column(db.Boolean, default=True)
    f_ouderleerlingen_email = db.Column(db.Boolean, default=True)


    def __setattr__(self, key, value):
        if key == 'school_lijst':
            if len(self.school_lijst) > 0:
                update_schools(self, value)
            else:
                add_schools(self, value)
            return
        super.__setattr__(self, key, value)


def add_student(data = {}):
    try:
        student = StudenIntake()
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(StudenIntake, k).expression.type.python_type == type(v) or isinstance(v, list):
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
                if getattr(StudenIntake, k).expression.type.python_type == type(v) or isinstance(v, list):
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
        q = StudenIntake.query
        for k, v in data.items():
            if hasattr(StudenIntake, k):
                q = q.filter(getattr(StudenIntake, k) == v)
        if order_by:
            q = q.order_by(getattr(StudenIntake, order_by))
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


def add_school(data = {}, commit=True):
    try:
        school = School()
        for k, v in data.items():
            if hasattr(school, k):
                if getattr(School, k).expression.type.python_type == type(v) or isinstance(v, StudenIntake):
                    setattr(school, k, v.strip() if isinstance(v, str) else v)
        db.session.add(school)
        if commit:
            db.session.commit()
        return school
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def add_schools(student, data={}):
    for s in data:
        s['student'] = student
        add_school(s, False)


def update_school(school, data={}, commit=True):
    try:
        for k, v in data.items():
            if hasattr(school, k):
                if getattr(School, k).expression.type.python_type == type(v) or isinstance(v, list):
                    setattr(school, k, v.strip() if isinstance(v, str) else v)
        if commit:
            db.session.commit()
        return school
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_schools(student, schools):
    for old_school in student.school_lijst:
        for new_school in schools:
            if old_school.jaar == new_school['jaar']:
                update_school(old_school, new_school, False)
                break


############ student overview list #########
def pre_filter():
    return db.session.query(StudenIntake)


def filter_data(query, filter):
    if filter and 'type' in filter[0] and filter[0]['type'] == 'checkbox':
        for cb in filter[0]['value']:
            query = query.filter(text(cb['id']), cb['checked'])
    for f in filter:
        if f['type'] == 'select' and f['value'] != 'none':
            query = query.filter(getattr(StudenIntake, f['name']) == (f['value'] == 'True'))
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(StudenIntake.s_first_name.like(search_string))
    search_constraints.append(StudenIntake.s_last_name.like(search_string))
    return search_constraints


