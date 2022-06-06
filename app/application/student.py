from app import log
from app.data import student as mstudent, settings as msettings, photo as mphoto
import app.data.settings
from app.application import formio as mformio, email as memail
import sys, datetime, base64
from app.application.settings import subscribe_handle_button_clicked


def delete_students(ids):
    mstudent.delete_students(ids)


# find the highest vsk number assigned to a student
def get_last_vsk_number():
    try:
        student = mstudent.get_students(order_by='-vsknummer', first=True)
        if student and student.vsknummer != '':
            return {"status": True, "data": student.vsknummer}
        else:
            start_number = msettings.get_configuration_setting('cardpresso-vsk-startnumber')
            return {"status": True, "data": start_number
                    }
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return {"status": False, "data": f'Error: {e}'}


# update students with no vsk number yet.  Start from the given number and increment for each student
# return the number of updated students
def update_vsk_numbers(vsknumber):
    try:
        vsknumber = int(vsknumber)
        changed_students = []
        students = mstudent.get_students({'vsknummer': ''})
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
        ret = get_last_vsk_number()
        if ret['data'] != '':
            ret = update_vsk_numbers(ret['data'])
            if ret['status']:
                log.info(f'vsk cron task, {ret["data"]} numbers updated')
            else:
                log.error(f'vsk cron task, error: {ret["data"]}')
        else:
            log.error('vsk cron task, error: no vsk numbers available')
            memail.compose_message('cardpresso-inform-emails', "SDH: Vsk nummers", "Waarschuwing, er zijn geen Vsk nummers toegekend (niet beschikbaar?)")


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
    photos = [p[1] for p in mphoto.get_photos_size()]
    for student in db_list:
        em = student.to_dict()
        if student.foto not in photos:
            em['overwrite_cell_color'] = [['foto', 'pink']]
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out
