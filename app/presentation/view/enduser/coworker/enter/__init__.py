from flask import Blueprint

enter = Blueprint('coworker.enter', __name__)

from . import views

