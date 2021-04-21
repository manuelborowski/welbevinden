from flask import Blueprint

end_user = Blueprint('guest', __name__)

from . import views

