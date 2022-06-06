from app import log, flask_app
from app.data import photo as mphoto
from app.application import settings as msettings
import base64, glob, os, sys


def get_photo(id):
    photo = mphoto.get_first_photo({"id": id})
    return base64.b64encode(photo.photo)


# https://www.putorius.net/mount-windows-share-linux.html#using-the-mountcifs-command
# on the linux server, mount the windows-share (e.g  mount.cifs //MyMuse/SharedDocs /mnt/cifs -o username=putorius,password=notarealpass,domain=PUTORIUS)
# in app/static, add a symlink to the the mounted windows share.  It is assumed all photo's are in the folder 'huidig'
# photo's are copied to the 'photos' folder when a photo does not exist or it's size changed
# sudo mount -t drvfs //10.10.0.211/sec /mnt/sec

mapped_photos_path = 'app/static/mapped_photos/huidig'
photos_path = 'app/static/photos/'

def get_photos():
    try:
        log.info("start import photo's")
        mapped_photos = glob.glob(f'{mapped_photos_path}/*jpg')
        nbr_new = 0
        nbr_updated = 0
        nbr_processed = 0
        nbr_deleted = 0

        photo_sizes = mphoto.get_photos_size()
        saved_photos = {p[1]: {'size': p[5], 'new': p[2], 'changed': p[3], 'delete': p[4]} for p in photo_sizes}

        for mapped_photo in mapped_photos:
            base_name = os.path.basename(mapped_photo)
            if base_name not in saved_photos:
                photo = open(mapped_photo, 'rb').read()     # new photo
                mphoto.add_photo({'filename': base_name, 'photo': photo}, commit=False)
                nbr_new += 1
            else:
                mapped_size = os.path.getsize(mapped_photo)
                if mapped_size != saved_photos[base_name]['size']:
                    photo = open(mapped_photo, 'rb').read()  # updated photo, different size
                    mphoto.update_photo(base_name, {'photo': photo, 'new': False, 'changed': True, 'delete': False}, commit=False)
                    nbr_updated += 1
                else:
                    if saved_photos[base_name]['new'] or saved_photos[base_name]['changed'] or saved_photos[base_name]['delete']:
                        mphoto.update_photo(base_name, {'new': False, 'changed': False, 'delete': False}, commit=False) # no update
                del(saved_photos[base_name])
            nbr_processed += 1
            if (nbr_processed % 100) == 0:
                log.info(f'get_photos: processed {nbr_processed} photo\'s...')
        for filename, item in saved_photos.items():
            if not saved_photos[filename]['delete']:
                mphoto.update_photo(filename, {'new': False, 'changed': False, 'delete': True}, commit=False)  # delete only when not already marked as delete
                nbr_deleted += 1
        mphoto.commit()
        log.info(f'get_new_photos: processed: {nbr_processed}, new {nbr_new}, updated {nbr_updated}, deleted {nbr_deleted}')
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def photo_cron_task(opaque):
    if msettings.get_configuration_setting('cron-enable-update-student-photo'):
        load_photos_from_su_data()


def load_photos_from_su_data(topic=None, opaque=None):
    with flask_app.app_context():
        get_photos()


msettings.subscribe_handle_button_clicked('button-load-photos', load_photos_from_su_data, None)
