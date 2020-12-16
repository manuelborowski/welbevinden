from flask import session
from flask_login import current_user
from app import login_manager, db
from app.data.models import User
from app import data


def filter(query_in):
    #If the logged in user is NOT administrator, display the data of the current user only
    if not current_user.is_at_least_admin:
        return query_in.filter(User.id==current_user.id)
    return query_in


# Set up user_loader
# @login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


def pre_filter():
    return db.session.query(User)


def search_data(search_string):
    search_constraints = []
    search_constraints.append(User.username.like(search_string))
    search_constraints.append(User.first_name.like(search_string))
    search_constraints.append(User.last_name.like(search_string))
    search_constraints.append(User.email.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out

