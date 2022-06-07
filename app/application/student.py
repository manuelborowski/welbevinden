from app import log
from app.data import student as mstudent, settings as msettings, photo as mphoto
import app.data.settings
from app.application import formio as mformio, email as memail
import sys, base64


def delete_students(ids):
    mstudent.delete_students(ids)


# find the first next vsk number, to be assigned to a student, or -1 when not found
def get_next_vsk_number():
    try:
        student = mstudent.get_students({'delete': False}, order_by='-vsknummer', first=True)
        if student and student.vsknummer != '':
            return {"status": True, "data": int(student.vsknummer) + 1}
        else:
            start_number = msettings.get_configuration_setting('cardpresso-vsk-startnumber')
            return {"status": True, "data": start_number}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return {"status": False, "data": f'Error: {e}'}


# update students with no vsk number yet.  Start from the given number and increment for each student
# return the number of updated students
def update_vsk_numbers(vsknumber):
    try:
        vsknumber = int(vsknumber)
        changed_students = []
        students = mstudent.get_students({'vsknummer': '', 'delete': False})
        nbr_updated = 0
        for student in students:
            changed_students.append({
                'vsknummer': str(vsknumber),
                'student': student,
                'changed': ['vsknummer']
            })
            vsknumber += 1
            nbr_updated += 1
        mstudent.update_students(changed_students)
        return {"status": True, "data": nbr_updated}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return {"status": False, "data": f'Error: {e}'}


def clear_vsk_numbers():
    students = mstudent.get_students()
    nbr_updated = 0
    for student in students:
        student.vsknummer = ''
        nbr_updated += 1
    mstudent.commit()
    return {"status": True, "data": nbr_updated}


def vsk_numbers_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-vsk-numbers'):
        # check if schooljaar has changed.  If so, clear all vsk numbers first
        student = mstudent.get_first_student({'delete': False, 'new': False, '-changed': ''})
        if student and 'schooljaar' in student.changed:
            ret = clear_vsk_numbers()
            log.info(f'vsk_numbers_cron_task: deleted {ret["data"]} vsk numbers')
        ret = get_next_vsk_number()
        if ret['status'] and ret['data'] > -1:
            ret = update_vsk_numbers(ret['data'])
            if ret['status']:
                log.info(f'vsk cron task, {ret["data"]} numbers updated')
            else:
                log.error(f'vsk cron task, error: {ret["data"]}')
        else:
            log.error('vsk cron task, error: no vsk numbers available')
            memail.compose_message('sdh-inform-emails', "SDH: Vsk nummers", "Waarschuwing, er zijn geen Vsk nummers toegekend (niet beschikbaar?)")


def deactivate_deleted_students():
    try:
        flag_list = []
        deleted_students = mstudent.get_students({"delete": True})
        for student in deleted_students:
            flag_list.append({'changed': '', 'delete': False, 'new': False, 'student': student, 'active': False})
        mstudent.flag_students(flag_list)
        log.info(f"deactivate_deleted_students: deactivated {len(deleted_students)}")
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def deactivate_deleted_students_cron_task(opaque):
    if msettings.get_configuration_setting('cron-deactivate-deleted-students'):
        deactivate_deleted_students()


############## formio #########################

def prepare_view_form(id, read_only=False):
    try:
        student = mstudent.get_first_student({"id": id})
        template = app.data.settings.get_json_template('student-formio-template')
        photo = mphoto.get_first_photo({'filename': student.foto})
        data = {"photo": base64.b64encode(photo.photo).decode('utf-8') if photo else ''}
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
        if student.foto_id == -1:
            em['overwrite_cell_color'] = [['foto', 'pink']]
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out


def get_nbr_photo_not_found():
    nbr_students_no_photo = mstudent.get_students({'foto_id': -1}, count=True)
    return nbr_students_no_photo