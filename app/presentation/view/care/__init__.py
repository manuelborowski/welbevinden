from flask import Blueprint

care = Blueprint('care', __name__)

from . import views
