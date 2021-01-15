from flask import Blueprint

reservation = Blueprint('reservation', __name__)

from . import views
