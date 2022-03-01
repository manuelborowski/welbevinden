from flask import flash, request
import datetime

stb_id = 'STB' #standby
act_id = 'ACT' #active
avl_id = 'AVL' #available

def filter_duplicates_out(keep_list, filter_list):
    keep_list.append(('disabled', '--------'))
    for i in filter_list:
        if not i in keep_list:
            keep_list.append(i)
    return keep_list

#It is possible to give an extra (exception) message
#The python UTF-8 string is encoded to html UTF-8
def flash_plus(message, e=None):
    message = message.replace('\n', '<br>')
    if e:
        flash((f'{message}<br><br>Details:<br>{e}'))
    else:
        flash((f'{message}'))

def button_save_pushed():
    return 'button' in request.form and request.form['button'] == 'save'


def request_valid_from():
    valid_from = None
    if 'valid_from' in request.values:
        valid_from = datetime.datetime.strptime(request.values['valid_from'], '%d-%m-%Y')
    return valid_from


def button_pressed(button=None):
    if button:
        return 'button-pressed' in request.values and request.values['button-pressed'] == button
    else:
        return request.values['button-pressed'] if 'button-pressed' in request.values else ''



