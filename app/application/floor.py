from app import db, log
from app.data.models import Floor
from app.data import utils as mutils

def add_floor(level, name='', info=''):
    try:
        floor = Floor.query.filter(Floor.level == level).all()
        if floor:
            log.warning(f'Floor {level} {name} already exists')
            return False
        floor = Floor(level=level, name=name, info=info)
        db.session.add(floor)
        db.session.commit()
    except Exception as e:
        mutils.raise_error(f'could not add floor {level}', e)
    return True

for k, v in Floor.Level.get_enum_list():
    add_floor(v)


