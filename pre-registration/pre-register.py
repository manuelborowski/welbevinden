import requests, json, time

WAIT_TIME = 1   #seconds
URL = 'http://localhost:5035'

def import_pre_register():
    with open('pre-reg-out.json',) as pre_reg_file:
        pre_reg = json.load(pre_reg_file)
        for i, item in enumerate(pre_reg):
            session = requests.Session()
            res = session.post(url=f'{URL}/api/register/add', data=json.dumps(item))
            status = json.loads(res.content)
            if status['status']:
                code = status['data']
                res = session.post(url=f'{URL}/api/register/done', data=json.dumps({'code': code}))
                status = json.loads(res.content)
                if status['status']:
                    res = session.post(url=f'{URL}/api/register/status/check', data=json.dumps({'code': code}))
                    status = json.loads(res.content)
                    if status['status']:
                        print(i, item['field_of_study'], item['child_first_name'], item['child_last_name'], item['indicator'], 'REGISTERED' if status['data'] else 'WAITING LIST')
            if not status['status'] and 'data' in status:
                print(status['data'])
            time.sleep(WAIT_TIME)

import_pre_register()
