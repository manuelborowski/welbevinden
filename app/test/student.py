import requests, json, time
from lorem_text import lorem
import names, random
from random import randrange
from datetime import timedelta
from datetime import datetime

WAIT_TIME = 0.2   #seconds
URL = 'http://localhost:5037'
# URL = 'https://opendag-inschrijvingen.ict.campussintursula.be'
nbr_words = 50


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second)).strftime('%d/%m/%Y')


def random_datetime(start, end):
    date = random_date(start, end)
    hour = randrange(0, 24)
    minute = randrange(0, 60)
    second = randrange(0, 60)
    datetime = f'{date} {hour}:{minute}:{second}'
    return datetime


def populate_students(nbr_students):
    for i in range(nbr_students):
        data = {
            's_first_name': names.get_first_name(),
            's_last_name': names.get_last_name(),
            's_code': str(i),
            's_date_of_birth': random_date(datetime(2005, 1, 1), datetime(2010, 12,31)),
            's_sex': random.choice(['man', 'vrouw']),

            'i_first_name': names.get_first_name(),
            'i_last_name': names.get_last_name(),
            'i_code': str(i+10000),
            'i_intake_date': random_datetime(datetime(2022, 1, 1), datetime(2022, 12,31)),

            'vorige_school': lorem.words(nbr_words),
            'vorig_clb': lorem.words(nbr_words),

            'f_gemotiveerd_verslag': random.choice([True, False]),
            'f_verslag_ontbindende_voorwaarden': random.choice([True, False]),
            'f_geen_verslag_specifieke_behoefte': random.choice([True, False]),

            'f_nood_aan_voorspelbaarheid': random.choice([True, False]),

            'thuissituatie': lorem.words(nbr_words),

            'schoolloopbaan': lorem.words(nbr_words),
            'advies_school': lorem.words(nbr_words),
            'definitieve_studiekeuze': lorem.words(nbr_words),

            'f_ass': random.choice([True, False]),
            'ass': lorem.words(nbr_words),
            'f_add': random.choice([True, False]),
            'add': lorem.words(nbr_words),
            'f_adhd': random.choice([True, False]),
            'adhd': lorem.words(nbr_words),
            'f_dcd': random.choice([True, False]),
            'dcd': lorem.words(nbr_words),
            'f_hoogbegaafd': random.choice([True, False]),
            'hoogbegaafd': lorem.words(nbr_words),
            'f_dyscalculie': random.choice([True, False]),
            'dyscalculie': lorem.words(nbr_words),
            'f_dyslexie': random.choice([True, False]),
            'dyslexie': lorem.words(nbr_words),
            'f_dysorthografie': random.choice([True, False]),
            'dysorthografie': lorem.words(nbr_words),
            'f_stos_dysfasie': random.choice([True, False]),
            'stos_dysfasie': lorem.words(nbr_words),
            'f_andere': random.choice([True, False]),
            'andere': lorem.words(nbr_words),
            'motoriek': lorem.words(nbr_words),
            'gezondheid': lorem.words(nbr_words),

            'groepsfunctioneren': lorem.words(nbr_words),
            'individueel_functioneren': lorem.words(nbr_words),
            'communicatie': lorem.words(nbr_words),

            'algemeen': lorem.words(nbr_words),
            'taalvaardigheid': lorem.words(nbr_words),
            'rekenvaardigheid': lorem.words(nbr_words),

            'ondersteunende_maatregelen': lorem.words(nbr_words),
            'schoolexterne_zorg': lorem.words(nbr_words),

        }
        session = requests.Session()
        res = session.post(url=f'{URL}/api/student/add?api_key=test33', data=json.dumps(data))
        status = json.loads(res.content)
        if status['status']:
            print (f'{i}: {status["data"]}')
        else:
            print(status['data'])
        time.sleep(WAIT_TIME)


def populate_students2(nbr_students):
    for i in range(nbr_students):
        data = {
            's_first_name': f's_first_name-{i}',
            's_last_name': f's_last_name-{i}',
            's_code': f's_code-{i}',
            's_date_of_birth': random_date(datetime(2005, 1, 1), datetime(2010, 12,31)),
            's_sex': random.choice(['m', 'v']),

            'i_first_name': f'i_first_name-{i}',
            'i_last_name': f'i_last_name-{i}',
            'i_code': f'i_code-{i+10000}',
            'i_intake_date': random_datetime(datetime(2022, 1, 1), datetime(2022, 12,31)),

            'vorige_school': f'vorige_school-{i}',
            'vorig_clb': f'vorig_clb-{i}',

            'f_gemotiveerd_verslag': random.choice([True, False]),
            'f_verslag_ontbindende_voorwaarden': random.choice([True, False]),
            'f_geen_verslag_specifieke_behoefte': random.choice([True, False]),

            'f_nood_aan_voorspelbaarheid': random.choice([True, False]),

            'thuissituatie': f'thuissituatie-{i}',

            'schoolloopbaan': f'schoolloopbaan-{i}',
            'advies_school': f'advies_school-{i}',
            'definitieve_studiekeuze': f'definitieve_studiekeuze-{i}',

            'f_ass': random.choice([True, False]),
            'ass': f'ass-{i}',
            'f_add': random.choice([True, False]),
            'add': f'add-{i}',
            'f_adhd': random.choice([True, False]),
            'adhd': f'adhd-{i}',
            'f_dcd': random.choice([True, False]),
            'dcd': f'dcd-{i}',
            'f_hoogbegaafd': random.choice([True, False]),
            'hoogbegaafd': f'hoogbegaafd-{i}',
            'f_dyscalculie': random.choice([True, False]),
            'dyscalculie': f'dyscalculie-{i}',
            'f_dyslexie': random.choice([True, False]),
            'dyslexie': f'dyslexie-{i}',
            'f_dysorthografie': random.choice([True, False]),
            'dysorthografie': f'dysorthografie-{i}',
            'f_stos_dysfasie': random.choice([True, False]),
            'stos_dysfasie': f'stos_dysfasie-{i}',
            'f_andere': random.choice([True, False]),
            'andere': f'andere-{i}',
            'motoriek': f'motoriek-{i}',
            'gezondheid': f'gezondheid-{i}',

            'groepsfunctioneren': f'groepsfunctioneren-{i}',
            'individueel_functioneren': f'individueel_functioneren-{i}',
            'communicatie': f'communicatie-{i}',

            'algemeen': f'algemeen-{i}',
            'taalvaardigheid': f'taalvaardigheid-{i}',
            'rekenvaardigheid': f'rekenvaardigheid-{i}',

            'ondersteunende_maatregelen': f'ondersteunende_maatregelen-{i}',
            'schoolexterne_zorg': f'schoolexterne_zorg-{i}',

        }
        session = requests.Session()
        res = session.post(url=f'{URL}/api/student/add', data=json.dumps(data))
        status = json.loads(res.content)
        if status['status']:
            print (f'{i}: {status["data"]}')
        else:
            print(status['data'])
        time.sleep(WAIT_TIME)

populate_students(1)
