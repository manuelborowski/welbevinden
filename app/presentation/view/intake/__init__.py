from flask import Blueprint

intake = Blueprint('intake', __name__)

from . import views
