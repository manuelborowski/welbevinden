from app.data.models import Room, Floor, EndUser, get_columns
from app.data import utils as mutils
from app import db, log

def get_room(owner, extract_columns=False):
    try:
        room = Room.query.filter(Room.code == owner.code).first()
        if room:
            if room.state == Room.State.E_CLOSED:
                room.state = Room.State.E_NEW
            return room
        else:
            room = add_room(owner)
            if extract_columns:
                return get_columns(room)
            return room
    except Exception as e:
        mutils.raise_error(f'could not find room for code {owner.full_name()}', e)
    return None


def add_room(owner):
    room = None
    try:
        floor = Floor.query.filter(Floor.level == owner.profile).first()
        room = Room(code=owner.code, floor=floor, name=owner.full_name())
        db.session.add(room)
        db.session.commit()
    except Exception as e:
        mutils.raise_error(f'could not add room: ', e)
    return room

