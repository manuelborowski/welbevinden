from app import flask_app
from app.application import utils as mutils


#called each time a request is received from the client.
@flask_app.context_processor
def inject_academic_year():
    test_server = mutils.return_common_info()
    return dict(test_server=test_server)

