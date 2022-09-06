from app import log
from app.application import settings as msettings
import xmlrpc.client, sys

PROPERTY_RFID = 'primary-card-number'

def update_student(student, data):
    try:
        url = msettings.get_configuration_setting('papercut-server-url')
        port = msettings.get_configuration_setting('papercut-server-port')
        token = msettings.get_configuration_setting('papercut-auth-token')
        with xmlrpc.client.ServerProxy(f'http://{url}:{port}/rpc/api/xmlrpc') as server:
            if 'rfid' in data:
                server.api.setUserProperty(token, student.username, PROPERTY_RFID, student.rfid)
        log.info(f'Update to papercut, {student.username} RFID {student.rfid}')
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
