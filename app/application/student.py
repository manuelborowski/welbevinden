from app import log
from app.data import student as mstudent, settings as msettings, photo as mphoto
import app.data.settings
from app.application import formio as mformio
import sys, datetime, base64
from app.application.settings import subscribe_handle_button_clicked


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


# find the highest vsk number assigned to a student
def get_last_vsk_number():
    student = mstudent.get_students(order_by='-vsknummer', first=True)
    return {"status": True, "data": student.vsknummer if student  and student.vsknummer else ''}


# update students with no vsk number yet.  Start from the given number and increment for each student
# return the number of updated students
def update_vsk_numbers(vsknumber):
    students = mstudent.get_students({'vsknummer': ''})
    nbr_updated = 0
    for student in students:
        student.vsknummer = vsknumber
        vsknumber += 1
        nbr_updated += 1
    mstudent.commit()
    return {"status": True, "data": nbr_updated}


def clear_vsk_numbers():
    students = mstudent.get_students()
    nbr_updated = 0
    for student in students:
        student.vsknummer = ''
        nbr_updated += 1
    mstudent.commit()
    return {"status": True, "data": nbr_updated}


############## formio forms #############
def prepare_add_form():
    try:
        template = app.data.settings.get_json_template('student-formio-template')
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


def prepare_edit_form(id, read_only=False):
    try:
        student = mstudent.get_first_student({"id": id})
        try:
            filename = student.foto.split('\\')[1]
        except:
            filename = student.foto
        template = app.data.settings.get_json_template('student-formio-template')
        photo = mphoto.get_first_photo({'filename': filename})
        data = {"photo": base64.b64encode(photo.photo).decode('utf-8')}
        template = mformio.prepare_for_edit(template, data)
        return {'template': template,
                'defaults': student.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e




############ student overview list #########
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
