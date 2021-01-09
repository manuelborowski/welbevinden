from flask import Blueprint

end_user = Blueprint('end_user', __name__)

from . import views

