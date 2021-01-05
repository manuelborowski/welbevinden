from app.data.models import Room, Floor, EndUser, ChatLine
from app.data import utils as mutils
from app import db, log
import datetime

def get_room(owner):
    try:
        room = Room.query.filter(Room.code == owner.code).first()
        if room:
            if room.state == Room.State.E_CLOSED:
                room.state = Room.State.E_NEW
            return room
        else:
            room = add_room(owner)
            room.history = []
            return room
    except Exception as e:
        mutils.raise_error(f'could not find room for code {owner.full_name()}', e)
    return None


def add_room(owner):
    room = None
    try:
        floor = Floor.query.filter(Floor.level == owner.profile).first()
        room = Room(code=owner.code, floor=floor, name=owner.full_name())
        room.guests.append(owner)
        db.session.add(room)
        db.session.commit()
    except Exception as e:
        mutils.raise_error(f'could not add room: ', e)
    return room

def add_chat_line(room_code, sender_code, initials, text):
    try:
        room = Room.query.filter(Room.code == room_code).first()
        if room:
            chat_line = ChatLine(owner_code=sender_code, initials=initials, text=text, timestamp=datetime.datetime.now(), room=room)
            db.session.add(chat_line)
            db.session.commit()
        else:
            log.error(f'add_chat_line: room with wode {room_code} not found')
    except Exception as e:
        mutils.raise_error(f'could not add chat line', e)
    return None


def get_history(room_code):
    history = []
    try:
        room = Room.query.join(ChatLine).filter(Room.code == room_code).order_by(ChatLine.timestamp).first()
        if room:
            history = [{'room': room.code, 'sender': l.owner_code, 'initials': l.initials, 'text': l.text} for l in  room.history]
        return history
    except Exception as e:
        mutils.raise_error(f'could not get history for for room code {room_code}', e)
    return history


def select_least_occupied_room(floor_level):
    try:
        rooms = Room.query.join(Floor).filter(Floor.level == floor_level).all()
        if rooms:
            room = rooms[0]
        return room
    except Exception as e:
        mutils.raise_error(f'could not get room with least number of guests for {floor_level}', e)
    return None




