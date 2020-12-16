from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_jsglue import JSGlue
from werkzeug.routing import IntegerConverter as OrigIntegerConvertor
import logging.handlers, os, sys
from functools import wraps


flask_app = Flask(__name__, instance_relative_config=True, template_folder='presentation/templates/')

#V1.0 : base version : only login and users.  Can be used to start other projects

@flask_app.context_processor
def inject_version():
    return dict(version='V1.0')

#enable logging
LOG_HANDLE = 'IDM'
log = logging.getLogger(LOG_HANDLE)

# local imports
from config import app_config

db = SQLAlchemy()
login_manager = LoginManager()

#The original werkzeug-url-converter cannot handle negative integers (e.g. asset/add/-1/1)  
class IntegerConverter(OrigIntegerConvertor):
    regex = r'-?\d+'
    num_convert = int


#support custom filtering while logging
class MyLogFilter(logging.Filter):
    def filter(self, record):
        record.username = current_user.username if current_user and current_user.is_active else 'NONE'
        return True

config_name = os.getenv('FLASK_CONFIG')
config_name = config_name if config_name else 'production'

#set up logging
LOG_FILENAME = os.path.join(sys.path[0], app_config[config_name].STATIC_PATH, 'log/idm-log.txt')
try:
    log_level = getattr(logging, app_config[config_name].LOG_LEVEL)
except:
    log_level = getattr(logging, 'INFO')
log.setLevel(log_level)
log.addFilter(MyLogFilter())
log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 * 1024, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(username)s - %(message)s')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)

log.info('start SAP')

flask_app.config.from_object(app_config[config_name])
flask_app.config.from_pyfile('config.py')

jsglue = JSGlue(flask_app)
db.app=flask_app  # hack :-(
db.init_app(flask_app)


def create_admin():
    from app.data.models import User
    find_admin = User.query.filter(User.username == 'admin').first()
    if not find_admin:
        admin = User(username='admin', password='admin', level=User.LEVEL.ADMIN, user_type=User.USER_TYPE.LOCAL)
        db.session.add(admin)
        db.session.commit()

flask_app.url_map.converters['int'] = IntegerConverter

login_manager.init_app(flask_app)
login_manager.login_message = 'Je moet aangemeld zijn om deze pagina te zien!'
login_manager.login_view = 'auth.login'

migrate = Migrate(flask_app, db)




if 'db' in sys.argv:
    from app.data import models
else:
    create_admin() # Only once

    #flask database migrate
    #flask database upgrade
    #uncheck when migrating database
    #return flapp

    #flapp.config['PROFILE'] = True
    #flapp.wsgi_app = ProfilerMiddleware(flapp.wsgi_app, restrictions=['flapp', 0.8])

    #decorator to grant access to admins only
    def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_at_least_admin:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view


    #decorator to grant access to at least supervisors
    def supervisor_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_at_least_supervisor:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view

    from app.presentation.view import auth, user
    flask_app.register_blueprint(auth.auth)
    flask_app.register_blueprint(user.user)

    @flask_app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @flask_app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @flask_app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500

    @flask_app.route('/500')
    def error_500():
        abort(500)


