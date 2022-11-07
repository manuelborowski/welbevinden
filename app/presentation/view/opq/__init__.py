from flask import Blueprint

opq = Blueprint('opq', __name__)

from . import views
