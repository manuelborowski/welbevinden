from app.data import utils as mutils, settings as msettings



#Needs to be called at the end of the HTTP request
def session_done():
    mutils.data_done()

def return_common_info():
    return msettings.get_test_server()
