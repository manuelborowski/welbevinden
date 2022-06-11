# l = ldap.initialize('ldap://x.x.x.x')
# l.simple_bind_s('xxx@su.local', 'pasword')
#  l.search_s("CN=firstname lastname,OU=Beheerders,OU=Accounts,DC=SU,DC=local", ldap.SCOPE_SUBTREE, attrlist=["cn"])
# l.modify_s("CN=firstname lastname,OU=Beheerders,OU=Accounts,DC=SU,DC=local", [(ldap.MOD_REPLACE, "info", [b"nieuwe info"])])
# wwwhomepage: leerlingnummer
# pager: rfid
# postofficebox: computer
# l.search_s("CN=1A,OU=Klassen,OU=Groepen,DC=SU,DC=local", ldap.SCOPE_SUBTREE, attrlist=["member"])
# l.search_s(b"CN=F\xc3\xa9 Dieltjens,OU=2020-2021,OU=Leerlingen,OU=Accounts,DC=SU,DC=local".decode("utf-8"), ldap.SCOPE_SUBTREE)
# https://social.technet.microsoft.com/wiki/contents/articles/5392.active-directory-ldap-syntax-filters.aspx
# filter : "(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))" enabled/active user
# filter : "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))" disabled/inactive user

# l.rename_s('CN=Evelien Merckx,OU=terug,OU=2020-2021,OU=Leerlingen,OU=Accounts,DC=SU,DC=local', 'CN=Evelien Merckx', "OU=2021-2022,OU=Leerlingen,OU=Accounts,DC=SU,DC=local")
# move evelien from 2020-2021/terug to 2021-2022

#all ou's under leerlingen:  l.search_s("OU=Leerlingen,OU=Accounts,DC=SU,DC=local", ldap.SCOPE_SUBTREE, "(objectCategory=Organizationalunit)")


# use ldap3 (pip install ldap3)
# from ldap3 import Server, Connection, SAFE_SYNC

# s = ldap3.Server('ldaps://x.x.x.x', use_ssl=True)
# ldap_s = ldap3.Connection(s, 'su.local\\<user>', '<pasword>', auto_bind=True, authentication=ldap3.NTLM)
# ldap3.extend.microsoft.modifyPassword.ad_modify_password(ldap_s, 'CN=manuel test,OU=manuel-test,OU=Leerlingen,OU=Accounts,DC=SU,DC=local', 'Azerty12', None)

# status, result, response, _ = conn.search('o=test', '(objectclass=*)')  # usually yo
# conn.add('OU=manuel-test,OU=Leerlingen,OU=Accounts,DC=SU,DC=local', 'organizationalunit') # add OU manuel-test
# ret = conn.search('OU=Leerlingen,OU=Accounts,DC=SU,DC=local', '(objectclass=*)')  returns true or false
# conn.response : return values returned
# conn.search('OU=Leerlingen,OU=Accounts,DC=SU,DC=local', '(objectclass=organizationalunit)', SUBTREE, attributes=ALL_ATTRIBUTES)
# move user to other OU
# ldap_s.modify("CN=manuel test,OU=manuel-test,OU=Leerlingen,OU=Accounts,DC=SU,DC=local", {'description': [(ldap3.MODIFY_REPLACE, 'dit is een test')]})
# conn.modify_dn('CN=Rik Fabri,OU=2018-2019,OU=Leerlingen,OU=Accounts,DC=SU,DC=local', 'CN=Rik Fabri', new_superior='OU=manuel-test,OU=Leerlingen,OU=Accounts,DC=SU,DC=local')
#  attributes = {'samaccountname': 's66666', 'wwwhomepage': '66666', 'name': 'manuel test', 'useraccountcontrol': 544, 'cn': 'manuel test', 'sn': 'test', 'l': 'manuel-6IT', 'description': 'manuel-test manuel-6IT', 'postalcode': '26-27', 'physicalDeliveryOfficeName': 'manuel-6IT', 'givenname': 'manuel', 'displayname': 'manuel test'}


from app import log
from app.data import student as mstudent
from app.data import settings as msettings

# from ldap3 import Server, Connection, SYNC
import ldap3, json

student_location_toplevel = 'OU=Leerlingen,OU=Accounts,DC=SU,DC=local'

check_properties_changed = ['naam', 'voornaam', 'klascode', 'schooljaar', 'rifd', 'computer']


def update_ad():
    try:
        log.info(('Start update to AD'))
        changed_schoolyear, prev_year, current_year =  msettings.get_changed_schoolyear()
        if changed_schoolyear: # keep a local copy of changed-schoolyear
            msettings.set_configuration_setting('ad-schoolyear-changed', True)
        changed_schoolyear = msettings.get_configuration_setting('ad-schoolyear-changed')

        ad_host = msettings.get_configuration_setting('ad-url')
        ad_login = msettings.get_configuration_setting('ad-login')
        ad_password = msettings.get_configuration_setting('ad-password')
        ldap_server = ldap3.Server(ad_host, use_ssl=True)
        ldap = ldap3.Connection(ldap_server, ad_login, ad_password, auto_bind=True, authentication=ldap3.NTLM)

        # cache active students, use leerlingnummer as key
        ad_active_students = {}
        res = ldap.search(student_location_toplevel, f'(&(objectclass=user)!(userAccountControl:1.2.840.113556.1.4.803:=2))', ldap3.SUBTREE, attributes=['cn', 'wwwhomepage'])
        if res:
            ad_active_students = {s['attributes']['wwwhomepage']: s for s in res.response if s['attributes']['wwwhomepage'] != []}
            log.info(f'AD: create active-students-cache, {len(ad_active_students)} entries')

        # cache klas

        # check if OU current year exists.  If not, create
        find_current_year_ou = ldap.search(student_location_toplevel, f'(&(objectclass=organizationalunit)(name={current_year}))', ldap3.SUBTREE)
        if not find_current_year_ou:
            res = ldap.add(f'OU={current_year},{student_location_toplevel}', 'organizationalunit')
            if res:
                log.info(f'AD: added new OU: {current_year}')
            else:
                log.error(f'AD error: could not add OU {current_year}, aborting...')
                ldap.unbind()
                return
        student_location_current_year = f'OU={current_year},{student_location_toplevel}'

        # check if new student already exists in AD (student left school and came back)
        # if so, activate and put in current OU
        new_students = mstudent.get_students({"new": True})
        new_students_to_add = []    # these students do not exist yet in AD, must be added
        log.info('AD: new students: if student is already in AD: activate and put in current year OU')
        for student in new_students:
            res = ldap.search(student_location_toplevel, f'(&(objectclass=user)(wwwhomepage={student.leerlingnummer}))', ldap3.SUBTREE, attributes=['cn', 'userAccountControl'])
            if res:
                dn = ldap.response[0]['dn']     # current OU
                cn = ldap.response[0]['attributes']['cn'] # student
                account_control = ldap.response[0]['attributes']['userAccountControl'] # to activate
                res = ldap.modify_dn(dn, cn, student_location_current_year) # move student to current year OU
                if not res:
                    log.error(f'AD error, could not move {cn} from {dn} to {student_location_current_year}')
                account_control &= 2  # clear bit 2 to activate
                res = ldap.modify(f'CN={cn},{student_location_current_year}', {'userAccountControl' : [(ldap3.MODIFY_REPLACE, [account_control])]})
                if not res:
                    log.error(f'AD error, could not activate {cn}')
            else:
                new_students_to_add.append(student)
        log.info('AD: add (create) new students to current year OU')

        # add new students to current OU
        object_class = ['top', 'person', 'organizationalPerson', 'user']
        for student in new_students_to_add:
            attributes = {'samaccountname': f's{student.leerlingnummer}', 'wwwhomepage': f'{student.leerlingnummer}',
                          'name': f'{student.naam} {student.voornaam}',
                          'useraccountcontrol': 544, 'pager': student.rfid,
                          'cn': f'{student.naam} {student.voornaam}',
                          'sn': student.naam,
                          'l': student.klascode,
                          'description': f'{student.schooljaar} {student.klascode}', 'postalcode': student.schooljaar,
                          'physicalDeliveryOfficeName': student.klascode, 'givenname': student.voornaam,
                          'displayname': f'{student.naam} {student.voornaam}'}
            res = ldap.add(f'CN={student.naam} {student.voornaam},{student_location_current_year}', object_class, attributes)
            if not res:
                log.error(f'AD: could not add new student with attributes: {attributes}')

        # check if there are students with valid, changed attributes.  If so, update the attributes
        # if required, move the students to the current OU
        changed_students = mstudent.get_students({"-changed": "", "new": False})
        if changed_students:
            for student in changed_students:
                changed = json.loads(student.changed)
                if list(set(check_properties_changed).intersection(changed)):
                    if student.leerlingnummer in ad_active_students:
                        changes = {}
                        if 'naam' in changed or 'voornaam' in changed:
                            changes.update({'name': [ldap3.MODIFY_REPLACE, (f'{student.naam} {student.voornaam}')],
                                          'cn': [ldap3.MODIFY_REPLACE, (f'{student.naam} {student.voornaam}')],
                                          'sn': [ldap3.MODIFY_REPLACE, (student.naam)],
                                          'givenname': [ldap3.MODIFY_REPLACE, (student.voornaam)],
                                          'displayname': [ldap3.MODIFY_REPLACE, (f'{student.naam} {student.voornaam}')]})
                        if 'rfid' in changed:
                            changes.update({'pager': [ldap3.MODIFY_REPLACE, (student.rfid)]})
                        if 'schooljaar' in changed or 'klascode' in changed:
                            changes.update({'description': [ldap3.MODIFY_REPLACE, (f'{student.schooljaar} {student.klascode}')],
                                          'postalcode': [ldap3.MODIFY_REPLACE, (student.schooljaar,)],
                                          'physicalDeliveryOfficeName': [ldap3.MODIFY_REPLACE, (student.klascode)]})
                        res = ldap.modify(ad_active_students[student.leerlingnummer]['dn'], changes)
                        if not res:
                            log.error(f'AD error: could not update changes of {student.leerlingnummer}: {changes}')
                        if 'schooljaar' in changed: # move to new OU
                            res = ldap.modify_dn(ad_active_students[student.leerlingnummer]['dn'],
                                                 ad_active_students[student.leerlingnummer]['cn'],
                                                 student_location_current_year)  # move student to current year OU
                            if not res:
                                log.error(f'AD error, could not move {student.leerlingnummer} from {ad_active_students[student.leerlingnummer]["dn"]} to {student_location_current_year}')
                    else:
                        log.error(f'AD error: student {student.leerlingnummer} is not active in AD')

        # new student, check if already in AD (use leerlingnummer as key).  If exists, use this object else create
        # changed student, update in AD (not klas and klasgroep).  If schooljaar changed, move to new OU
        # deleted students, deactivate in AD

        #new or changed student, move to correct klas and klasgroep

        ldap.unbind()
        msettings.set_configuration_setting('ad-schoolyear-changed', False)
        log.info(f'update_ad: processed ')
    except Exception as e:
        log.error(f'update from wisa error: {e}')



def ad_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-student-ad'):
        update_ad()

