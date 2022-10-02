from app import log, flask_app
from app.data import student as mstudent, photo as mphoto, cardpresso as mcardpresso
from app.application import settings as msettings, email as memail
import sys, json, datetime


# remark; for contactless operations (RFID), use Springcard crazywriter Contactless 0 as encoder

def delete_badges(ids):
    mcardpresso.delete_badges(ids)
    log.info(f"done deleting badges: {ids}")


# indicates which badge property is required
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
        saved_photos = {p.id : p.photo for p in mphoto.get_photos()}
        for student_id in student_ids:
            student = mstudent.get_first_student({'id': student_id})
            if student:
                badge = mcardpresso.get_first_badge({'leerlingnummer': student.leerlingnummer})
                if badge:
                    delete_badges.append(badge.id)
                photo = saved_photos[student.foto_id] if student.foto_id in saved_photos else None
                if photo:
                    data = {'photo': photo}
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


def new_badges_cron_task(opaque=None):
    process_new_badges()


check_properties_changed = ['middag', 'vsknummer', 'photo', 'schooljaar', 'klascode', 'klasgroep']


def process_new_badges(topic=None, opaque=None):
    try:
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
                old_badges = mcardpresso.get_badges(data)
                ids = [b.id for b in old_badges]
                mcardpresso.delete_badges(ids)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


msettings.subscribe_button_clicked('button-new-badges', process_new_badges, None)


def check_for_new_rfid():
    try:
        changed_students = []
        deleted_badges = []
        badges = mcardpresso.get_badges({'changed': '["rfid"]'})
        if badges:
            saved_students = {s.leerlingnummer: s for s in mstudent.get_students({'delete': False})}
            for badge in badges:
                if badge.rfid != '':
                    if badge.leerlingnummer in saved_students:
                        new_rfid = badge.rfid.upper().replace('Q', 'A')
                        changed_students.append({'changed': ['rfid'], 'rfid': new_rfid, 'student': saved_students[badge.leerlingnummer]})
                        log.info(f'{sys._getframe().f_code.co_name}: new rfid {new_rfid} for {badge.leerlingnummer}')
                    else:
                        log.info(f'{sys._getframe().f_code.co_name}: {badge.leerlingnummer} not found')
                    deleted_badges.append(badge.id)
            if changed_students:
                mstudent.change_students(changed_students)
            if deleted_badges:
                mcardpresso.delete_badges(deleted_badges)
        log.info(f'check_for_new_rfid: updated {len(changed_students)} rfids of students')
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return {"status": False, "data": f'generic error {e}'}


def new_rfid_to_database_cron_task(opaque=None):
    rfid_code = msettings.get_configuration_setting('test-rfid-start-code')
    if rfid_code != '' and '#' not in rfid_code:
        try:
            code = int(rfid_code, 16)
            badges = mcardpresso.get_badges()
            for badge in badges:
                badge.rfid = hex(code)[2:]
                badge.changed = '["rfid"]'
                code += 1
            mcardpresso.commit()
            msettings.set_configuration_setting('test-rfid-start-code', hex(code)[2:])
            log.info('new_rfid_to_database_cron_task: test: inserted dummy rfid codes')
        except:
            log.error(f'new_rfid_to_database_cron_task: error, not a valid hex rfid-code {rfid_code}')
            pass
    check_for_new_rfid()

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



