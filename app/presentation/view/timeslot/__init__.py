from flask import Blueprint

timeslot = Blueprint('timeslot', __name__)

from . import views
