from flask import Blueprint

enduser = Blueprint('enduser', __name__)

from . import views

