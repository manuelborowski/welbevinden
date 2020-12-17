from flask import Blueprint

enter = Blueprint('guest.enter', __name__)

from . import views

