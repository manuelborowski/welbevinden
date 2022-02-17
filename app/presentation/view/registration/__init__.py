from flask import Blueprint

reservation = Blueprint('registration', __name__)

from . import views
