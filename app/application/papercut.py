from app import log, flask_app
from app.data import staff as mstaff
from app.application import settings as msettings
import xmlrpc.client, sys

PROPERTY_RFID = 'primary-card-number'

def update_student(student, data):
    try:
        update_property(student.username, data)
    except Exception as e:
        raise e


def update_staff(staff, data):
    try:
        update_property(staff.code, data)
    except Exception as e:
        raise e


def update_property(username, data):
    try:
        url = msettings.get_configuration_setting('papercut-server-url')
        port = msettings.get_configuration_setting('papercut-server-port')
        token = msettings.get_configuration_setting('papercut-auth-token')
        with xmlrpc.client.ServerProxy(f'http://{url}:{port}/rpc/api/xmlrpc') as server:
            if 'rfid' in data:
                server.api.setUserProperty(token, username, PROPERTY_RFID, data['rfid'])
        log.info(f'Update to papercut, {username} RFID {data}')
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def load_staff_rfid_codes(topic=None, opaque=None):
    try:
        url = msettings.get_configuration_setting('papercut-server-url')
        port = msettings.get_configuration_setting('papercut-server-port')
        token = msettings.get_configuration_setting('papercut-auth-token')
        staffs = mstaff.get_staffs()
        nbr_found = 0
        nbr_not_found = 0
        with xmlrpc.client.ServerProxy(f'http://{url}:{port}/rpc/api/xmlrpc') as server:
            for staff in staffs:
                try:
                    rfid = server.api.getUserProperty(token, staff.code, PROPERTY_RFID)
                    staff.rfid = rfid.upper()
                    log.info(f'{sys._getframe().f_code.co_name}, {staff.code} has rfid {rfid}')
                    nbr_found += 1
                except:
                    log.info(f'{sys._getframe().f_code.co_name}, {staff.code} is not present in papercut')
                    nbr_not_found += 1
        log.info(f'{sys._getframe().f_code.co_name}: gevonden in papercut {nbr_found}, niet gevonden {nbr_not_found}')
        mstaff.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e



msettings.subscribe_handle_button_clicked('papercut-load-rfid-event', load_staff_rfid_codes, None)