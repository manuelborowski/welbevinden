from app.data.models import InfoItem, Floor
from app import db, log
from app.data import utils as mutils


def add_info_item(floor, type, item, thumbnail, text, active=True):
    try:
        item = InfoItem(floor=floor, type=type, item=item, thumbnail=thumbnail, text=text, active=active)
        db.session.add(item)
        db.session.commit()
        log.info(f'Item {floor.level} {type} {item} {thumbnail} added')
    except Exception as e:
        mutils.raise_error('could not add info item', e)
    return True

def get_info_items(floor_level):
    try:
        floor = Floor.query.filter(Floor.level == floor_level).first()
        items = InfoItem.query.filter(InfoItem.floor == floor, InfoItem.active == True).all()
        return items
    except Exception as e:
        mutils.raise_error('could not add end user', e)
    return True



# floor = Floor.query.filter(Floor.level == Floor.Level.E_CLB).first()
# add_info_item(floor, InfoItem.Type.E_MP4, 'horses-item-1.mp4', 'horse-thumb-1.jpg', 'paarden in de natuur')



