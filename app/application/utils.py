from app.data import utils as mutils, settings as msettings, models as mmodels


#Needs to be called at the end of the HTTP request
def session_done():
    mutils.data_done()

def return_common_info():
    return msettings.get_test_server()

def flatten(sqlalchemy_object):
    return mmodels.get_columns(sqlalchemy_object)
