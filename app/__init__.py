from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_jsglue import JSGlue
from werkzeug.routing import IntegerConverter as OrigIntegerConvertor
import logging.handlers, os, sys
from functools import wraps
from flask_apscheduler import APScheduler
from flask_mail import Mail


flask_app = Flask(__name__, instance_relative_config=True, template_folder='presentation/templates/')

# Configuration files...
from config import app_config
config_name = os.getenv('FLASK_CONFIG')
config_name = config_name if config_name else 'production'
flask_app.config.from_object(app_config[config_name])
flask_app.config.from_pyfile('config.py')

# V0.1: copy from school-data-hub V0.60
# V0.2: added school specific settings
# V0.3: added survey
# V0.4: updated formio-create-components: take attributes into account.  Added functionality to upload/clear leerlingenlijst
# V0.5: creating the survey form for different scenarios is ok
# V0.6: bugfix formio preparation (remove obsolete components).  Ouders may sent in 2 surveys
# V0.7: switched to 5 user levels.  Re-implemented row_detail (datatables).  Implemented survey-question-overview.
# Datatables; make it possible to create columns from json-data from single-database column.  Use 4 survey templates iso 1.
# V0.8: suppress persistent-filter-settings if required.  Introduced filters
# V0.9: big update.  Removed obsolete files.  datatables-configuration; switched to object, cleaned up processing of data from database.
# V0.10: extracted overview-per-question from survey-view.  Added functionality to color the selected menu-item
# V0.11: small bugfixes.
# V0.12: implemented overview-per-student.  Implemented different user-levels.
# V0.13: updated survey-page
# V0.14: update requirements.txt
# V0.15: bugfixes when database is empty
# V0.16: when no leerlingen are loaded, do not show list of leerlingen for second survey.  Add add_survey api
# V0.17: apply default filter settings when a page is loaded
# V0.18: made string_cache an object.  Extended question-types with a type that connects an open question with a previous muliple-choice question.  It is possible to export the overview-per-student
# V0.19: update header-image.  Added a survey-active-window
# V0.20: small bugfix


@flask_app.context_processor
def inject_defaults():
    return dict(version='@ 2022 MB. V0.20', title=flask_app.config['HTML_TITLE'], site_name=flask_app.config['SITE_NAME'])


#  enable logging
log = logging.getLogger(flask_app.config['LOG_HANDLE'])


db = SQLAlchemy()
login_manager = LoginManager()


#  The original werkzeug-url-converter cannot handle negative integers (e.g. asset/add/-1/1)
class IntegerConverter(OrigIntegerConvertor):
    regex = r'-?\d+'
    num_convert = int


# support custom filtering while logging
class MyLogFilter(logging.Filter):
    def filter(self, record):
        record.username = current_user.username if current_user and current_user.is_active else 'NONE'
        return True


# set up logging
log_werkzeug = logging.getLogger('werkzeug')
log_werkzeug.setLevel(flask_app.config['WERKZEUG_LOG_LEVEL'])
# log_werkzeug.setLevel(logging.ERROR)

LOG_FILENAME = os.path.join(sys.path[0], app_config[config_name].STATIC_PATH, f'log/{flask_app.config["LOG_FILE"]}.txt')
try:
    log_level = getattr(logging, app_config[config_name].LOG_LEVEL)
except:
    log_level = getattr(logging, 'INFO')
log.setLevel(log_level)
log.addFilter(MyLogFilter())
log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1024 * 1024, backupCount=20)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(username)s - %(message)s')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)

log.info(f"start {flask_app.config['SITE_NAME']}")

jsglue = JSGlue(flask_app)
db.app = flask_app  #  hack:-(
db.init_app(flask_app)


def create_admin():
    try:
        from app.data.user import User
        find_admin = User.query.filter(User.username == 'admin').first()
        if not find_admin:
            admin = User(username='admin', password='admin', level=User.LEVEL.ADMIN, user_type=User.USER_TYPE.LOCAL)
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


flask_app.url_map.converters['int'] = IntegerConverter
login_manager.init_app(flask_app)
login_manager.login_message = 'Je moet aangemeld zijn om deze pagina te zien!'
login_manager.login_view = 'auth.login'

migrate = Migrate(flask_app, db)

# configure e-mailclient
email = Mail(flask_app)
send_emails = False
flask_app.extensions['mail'].debug = 0

SCHEDULER_API_ENABLED = True
ap_scheduler = APScheduler()
ap_scheduler.init_app(flask_app)
ap_scheduler.start()

if 'db' in sys.argv:
    from app.data import models
else:
    create_admin()  #  Only once

    # decorator to grant access to admins only
    def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_at_least_admin:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view


    # decorator to grant access to at least supervisors
    def instellen_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_at_least_instellen:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view

    from app.presentation.view import auth, user, settings,  api, survey, opq, ops
    flask_app.register_blueprint(api.api)
    flask_app.register_blueprint(auth.auth)
    flask_app.register_blueprint(user.user)
    flask_app.register_blueprint(settings.settings)
    flask_app.register_blueprint(survey.survey)
    flask_app.register_blueprint(opq.opq)
    flask_app.register_blueprint(ops.ops)

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


