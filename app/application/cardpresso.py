from app import log
from app.data import student as mstudent, settings as msettings, photo as mphoto, cardpresso as mcardpresso
import app.data.settings
from app.application import formio as mformio
import sys, datetime


def add_student(data):
    try:
        data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
        data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
        student = mstudent.add_student(data)
        log.info(f"Add care: {student.s_last_name} {student.s_first_name}, {data}")
        return {"status": True, "data": {'id': student.id}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def update_student(data):
    try:
        student = mstudent.get_first_student({'id': data['id']})
        if student:
            del data['id']
            data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
            data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
            student = mstudent.update_student(student, data)
            if student:
                log.info(f"Update care: {student.s_last_name} {student.s_first_name}, {data}")
                return {"status": True, "data": {'id': student.id}}
        return {"status": False, "data": "Er is iets fout gegaan"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def delete_students(ids):
    mstudent.delete_students(ids)


def add_new_badges(student_ids):
    try:
        nbr_added = 0
        nbr_already_present = 0
        for student_id in student_ids:
            student = mstudent.get_first_student({'id': student_id})
            cardpresso_student = mcardpresso.get_first_student({'leerlingnummer': student.leerlingnummer})
            if not cardpresso_student:
                if student:
                    try:
                        filename = student.foto.split('\\')[1]
                    except:
                        filename = student.foto
                    photo = mphoto.get_first_photo({'filename': filename})
                    data = {
                        'naam': student.naam,
                        'voornaam': student.voornaam,
                        'leerlingnummer': student.leerlingnummer,
                        'middag': student.middag,
                        'vsknummer': student.vsknummer,
                        'rfid': student.rfid,
                        'geboortedatum':  mformio.date_to_datestring(student.geboortedatum),
                        'straat': student.straat,
                        'huisnummer': student.huisnummer,
                        'busnummer': student.busnummer,
                        'gemeente': student.gemeente,
                        'schoolnaam': student.schoolnaam,
                        'schooljaar': student.schooljaar,
                        'klascode': student.klascode,
                        'photo': photo.photo,
                    }
                    cardpresso = mcardpresso.add_student(data)
                    if cardpresso:
                        log.info(f"Update cardpresso: {data}")
                        nbr_added += 1
            else:
                nbr_already_present += 1
        return {"status": True, "data": f"{len(student_ids)} leerlingen behandeld, {nbr_added} toegevoegd, {nbr_already_present} waren al toegevoegd"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


############## formio forms #############
def prepare_add_form():
    try:
        template = app.data.settings.get_json_template('care-formio-template')
        now = datetime.datetime.now()
        return {'template': template,
                'defaults': {
                        'i_intake_date': mformio.datetime_to_datetimestring(now),
                        's_code' : msettings.get_and_increment_default_student_code()
                    }
                }
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_form(id, read_only=False, pdf=False):
    try:
        student = mstudent.get_first_student({"id": id})
        template = app.data.settings.get_json_template('care-formio-template')
        template = mformio.prepare_for_edit(template, student.to_dict(), pdf)
        return {'template': template,
                'defaults': student.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e




############ badges overview list #########
def format_data(db_list):
    out = []
    for student in db_list:
        em = student.to_dict()
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out



