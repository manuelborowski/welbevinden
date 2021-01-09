from flask import Blueprint

register = Blueprint('enduser.register', __name__)

from . import views

