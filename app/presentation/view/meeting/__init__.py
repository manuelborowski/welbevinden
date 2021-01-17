from flask import Blueprint

meeting = Blueprint('meeting', __name__)

from . import views
