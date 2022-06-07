from app import log, flask_app
from app.data import student as mstudent, photo as mphoto, settings as msettings
from app.data.utils import belgische_gemeenten
from app.application import warning as mwarning
from app.application.settings import subscribe_handle_button_clicked
import datetime
import json, requests


def read_from_wisa_database(local_file=None, max=0):
    try:
        log.info('start import from wisa')
        if local_file:
            log.info(f'Reading from local file {local_file}')
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
        saved_photos = {p[1]: p[0] for p in mphoto.get_photos_size()}
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
            item['foto_id'] = saved_photos[item['foto']] if item['foto'] in saved_photos else -1
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
                    update_properties.extend(['delete', 'new'])
                    item['changed'] = update_properties # student already present, but is changed
                    changed_list.append(item)
                else:
                    flag_list.append({'changed': '', 'delete': False, 'new': False, 'student': student}) # student already present, no change
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
        mstudent.flag_students(flag_list)
        log.info(f'read_from_wisa_database: processed {nbr_processed}, new {len(new_list)}, updated {len(changed_list)}, deleted {nbr_deleted}')
    except Exception as e:
        log.error(f'update from wisa error: {e}')


def load_from_wisa(topic=None, opaque=None):
    with flask_app.app_context():
        wisa_files = msettings.get_list('test-wisa-json-list')
        if wisa_files:  # test with wisa files
            current_wisa_file = msettings.get_configuration_setting('test-wisa-current-json')
            if current_wisa_file == '' or current_wisa_file not in wisa_files:
                current_wisa_file = wisa_files[0]
            else:
                new_index = wisa_files.index(current_wisa_file) + 1
                if new_index >= len(wisa_files):
                    new_index = 0
                current_wisa_file = wisa_files[new_index]
            msettings.set_configuration_setting('test-wisa-current-json', current_wisa_file)
            read_from_wisa_database(local_file=current_wisa_file)
        else:
            # read_from_wisa_database(max=10)
            read_from_wisa_database()


subscribe_handle_button_clicked('button-load-from-wisa', load_from_wisa, None)


def wisa_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-student-from-wisa'):
        load_from_wisa()

#to have access to the photo's, mount the windowsshare
#sudo apt install keyutils


