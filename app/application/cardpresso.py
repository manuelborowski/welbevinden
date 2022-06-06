from app import log, flask_app
from app.data import student as mstudent, photo as mphoto, cardpresso as mcardpresso
from app.application import settings as msettings, email as memail
import sys, json, datetime


def delete_badges(ids):
    data = [{"id": id} for id in ids]
    mcardpresso.delete_badges(data)


# indicates which badge property is reaquired
badge_properties = {
    'naam': True,
    'voornaam': True,
    'leerlingnummer': True,
    'middag': False,
    'vsknummer': True,
    'geboortedatum': True,
    'straat': True,
    'huisnummer': True,
    'busnummer': False,
    'gemeente': True,
    'schoolnaam': True,
    'schooljaar': True,
    'klascode': True
}

def add_badges(student_ids):
    try:
        nbr_added = 0
        nbr_no_photo = 0
        nbr_empty_propery = 0
        delete_badges = []
        for student_id in student_ids:
            student = mstudent.get_first_student({'id': student_id})
            if student:
                badge = mcardpresso.get_first_badge({'leerlingnummer': student.leerlingnummer})
                if badge:
                    delete_badges.append({"id":badge.id})
                photo = mphoto.get_first_photo({'filename': student.foto})
                if photo:
                    data = {'photo': photo.photo}
                    student_dict = student.to_dict()
                    for p, r in badge_properties.items():
                        if r and student_dict[p] != '' or not r:
                            data.update({p: student_dict[p]})
                        else:
                            data = {}
                            break
                    if data:
                        badge = mcardpresso.add_badge(data)
                        if badge:
                            log.info(f"New badge: {student.naam} {student.voornaam} {student.leerlingnummer}")
                            nbr_added += 1
                    else:
                        log.error(f"New badge: {student.naam} {student.voornaam} {student.leerlingnummer} not all properties are valid")
                        nbr_empty_propery += 1
                else:
                    log.error(f"New badge: {student.naam} {student.voornaam} {student.leerlingnummer} has no valid photo")
                    nbr_no_photo += 1
            else:
                log.error(f"add_badges: student with id {student_id} not found")
        if delete_badges:
            mcardpresso.delete_badges(delete_badges)

        message = f"{len(student_ids)} leerlingen behandeld, {nbr_added} toegevoegd, {nbr_no_photo} hebben geen foto, {nbr_empty_propery} hebben ongeldige velden"
        memail.compose_message('cardpresso-inform-emails', "SDH: wijziging in Cardpresso", message)
        log.info(f'add_bages: {message}')
        return {"status": True, "data": message}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(f"add_badges: {student_ids}")
        return {"status": False, "data": f'generic error {e}'}


def badges_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-student-badge'):
        process_new_badges()

check_properties_changed = ['middag', 'vsknummer', 'photo', 'schooljaar']

def process_new_badges(topic=None, opaque=None):
    with flask_app.app_context():
        new_students = mstudent.get_students({'new': True})
        if new_students:
            ids = [student.id for student in new_students]
            add_badges(ids)
        updated_students = mstudent.get_students({'-changed': '', 'new': False})  # find students with changed property not equal to '' and not new
        if updated_students:
            ids = []
            for student in updated_students:
                changed = json.loads(student.changed)
                if list(set(check_properties_changed).intersection(changed)):
                    ids.append(student.id)
            if ids:
                add_badges(ids)
        deleted_students = mstudent.get_students({'delete': True})
        if deleted_students:
            data = [{"leerlingnummer": s.leerlingnummer } for s in deleted_students]
            mcardpresso.delete_badges(data)


msettings.subscribe_handle_button_clicked('button-new-badges', process_new_badges, None)


############ badges overview list #########
def format_data(db_list):
    out = []
    for item in db_list:
        em = item.to_dict()
        em.update({
            'row_action': item.id,
            'DT_RowId': item.id
        })
        out.append(em)
    return out



