from app import log
from app.data import settings as msettings, staff as mstaff
import app.data.settings
from app.application import util as mutil
import sys, base64


def delete_staffs(ids):
    mstaff.delete_staffs(ids)


# do not deactivate, but delete
def deactivate_deleted_staff_cron_task(opaque):
    if msettings.get_configuration_setting('cron-deactivate-deleted-staff'):
        try:
            deleted_staffs = mstaff.get_staffs({"delete": True})
            mstaff.delete_staffs(staffs=deleted_staffs)
            log.info(f"deleted {len(deleted_staffs)} staffs")
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')

############## api ####################
def get_fields():
    try:
        return mstaff.get_columns()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return False


def get_staffs(options=None):
    try:
        fields, filters = mutil.process_api_options(options)
        staffs = mstaff.get_staffs(data=filters, fields=fields)
        if fields:
            out = [dict(zip(fields, s)) for s in staffs]
        else:
            out = [s.to_dict() for s in staffs]
        return out
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


############## formio #########################
def prepare_view_form(id, read_only=False):
    try:
        pass
        # staff = mstaff.get_first_staff({"id": id})
        # template = app.data.settings.get_json_template('staff-formio-template')
        # photo = mphoto.get_first_photo({'filename': staff.foto})
        # data = {"photo": base64.b64encode(photo.photo).decode('utf-8') if photo else ''}
        # template = mformio.prepare_for_edit(template, data)
        # return {'template': template,
        #         'defaults': staff.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


############ datatables: staff overview list #########
def format_data(db_list):
    out = []
    for staff in db_list:
        em = staff.to_dict()
        em.update({
            'row_action': staff.id,
            'DT_RowId': staff.id
        })
        out.append(em)
    return out
