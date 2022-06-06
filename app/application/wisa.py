from app import log, flask_app
from app.data import student as mstudent
from app.data.utils import belgische_gemeenten
from app.application import settings as msettings, warning as mwarning
import datetime
import json, requests


def read_from_wisa_database(local_file=None, max=0):
    try:
        log.info('start import from wisa')
        if local_file:
            response_text = open(local_file).read()
        else:
            login = msettings.get_configuration_setting('wisa-login')
            password = msettings.get_configuration_setting('wisa-password')
            url = msettings.get_configuration_setting('wisa-url')
            werkdatum = str(datetime.date.today())
            url = f'{url}&werkdatum={werkdatum}&&_username_={login}&_password_={password}'
            response_text = requests.get(url).text
        # The query returns with the keys in uppercase.  Convert to lowercase first
        keys = mstudent.get_columns()
        for key in keys:
            response_text = response_text.replace(f'"{key.upper()}"', f'"{key}"')
        data = json.loads(response_text)

        # deactivate deleted students first
        flag_list = []
        deleted_students = mstudent.get_students({"delete": True})
        nbr_deactivated = len(deleted_students)
        for student in deleted_students:
            flag_list.append({'changed': '', 'delete': False, 'new': False, 'student': student, 'active': False})
        mstudent.flag_wisa_students(flag_list)

        saved_students = {}
        students = mstudent.get_students()
        if students:
            saved_students = {s.rijksregisternummer: s for s in students}
        new_list = []
        changed_list = []
        flag_list = []
        nbr_deleted = 0
        nbr_processed = 0
        for item in data:  #clean up, remove leading and trailing spaces
            for k, v in item.items():
                item[k] = v.strip()
        for item in data:
            orig_geboorteplaats = None
            if "," in item['geboorteplaats'] or "-" in item['geboorteplaats'] and item['geboorteplaats'] not in belgische_gemeenten:
                if "," in item['geboorteplaats']:   # sometimes, geboorteplaats is mis-used to also include geboorteland.
                    gl = item['geboorteplaats'].split(",")
                else:
                    gl = item['geboorteplaats'].split("-")
                orig_geboorteplaats = item['geboorteplaats']
                item['geboorteplaats'] = gl[0].strip()
                item['geboorteland'] = gl[1].strip()
            item['inschrijvingsdatum'] = datetime.datetime.strptime(item['inschrijvingsdatum'].split(' ')[0], '%Y-%m-%d').date()
            item['geboortedatum'] = datetime.datetime.strptime(item['geboortedatum'].split(' ')[0], '%Y-%m-%d').date()
            try:
                item['foto'] = item['foto'].split('\\')[1]
            except:
                pass
            try:
                item['klasnummer'] = int(item['klasnummer'])
            except:
                item['klasnummer'] = 0
            try:
                item['schooljaar'] = item['schooljaar'].split(' ')[1]
            except:
                pass
            if item['rijksregisternummer'] in saved_students:
                update_properties = []
                student = saved_students[item['rijksregisternummer']]
                for k, v in item.items():
                    if v != getattr(student, k):
                        update_properties.append(k)
                item['student'] = student
                item['delete'] = False
                item['new'] = False
                if update_properties:
                    item['changed'] = update_properties # student already present, but is changed
                    changed_list.append(item)
                else:
                    item['changed'] = ''      # student already present, no change
                    flag_list.append({'changed': '', 'delete': False, 'new': False, 'student': student})
                del(saved_students[item['rijksregisternummer']])
            else:
                if orig_geboorteplaats:
                    mwarning.new_warning(f'Leerling met leerlingnummer {item["leerlingnummer"]} heeft mogelijk een verkeerde geboorteplaats/-land: {orig_geboorteplaats}')
                    log.info(f'Leerling met leerlingnummer {item["leerlingnummer"]} heeft mogelijk een verkeerde geboorteplaats/-land: {orig_geboorteplaats}')
                new_list.append(item)  # new student
            nbr_processed += 1
            if max > 0 and nbr_processed >= max:
                break
        for k, v in saved_students.items(): # student not present in wisa anymore
            if not v.delete:
                flag_list.append({'changed': '', 'delete': True, 'new': False, 'student': v})
                nbr_deleted += 1
        mstudent.add_students(new_list)
        mstudent.update_students(changed_list, overwrite=True) # previous changes are lost
        mstudent.flag_wisa_students(flag_list)
        log.info(f'read_from_wisa_database: processed {nbr_processed}, new {len(new_list)}, updated {len(changed_list)}, deleted {nbr_deleted}, deactivated {nbr_deactivated}')
    except Exception as e:
        log.error(f'update from wisa error: {e}')


def load_from_wisa(topic=None, opaque=None):
    with flask_app.app_context():
        # read_from_wisa_database(max=10)
        read_from_wisa_database()


msettings.subscribe_handle_button_clicked('button-load-from-wisa', load_from_wisa, None)


def wisa_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-student-from-wisa'):
        load_from_wisa()

#to have access to the photo's, mount the windowsshare
#sudo apt install keyutils


