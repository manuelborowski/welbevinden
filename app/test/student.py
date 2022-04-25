import requests, json, time
from lorem_text import lorem
import names, random
from random import randrange
from datetime import timedelta
from datetime import datetime

WAIT_TIME = 0.2   #seconds
URL = 'http://localhost:5000'
# URL = 'https://opendag-inschrijvingen.ict.campussintursula.be'
nbr_words = 400


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second)).strftime('%Y-%m-%d')


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
            'i_intake_date': random_date(datetime(2022, 1, 1), datetime(2022, 12,31)),

            'vorige_school': lorem.words(nbr_words),
            'vorig_clb': lorem.words(nbr_words),

            'f_gemotiveerd_verslag': random.choice([True, False]),
            'f_verslag_ontbindende_voorwwarden': random.choice([True, False]),
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
            'f_discalculie': random.choice([True, False]),
            'discalculie': lorem.words(nbr_words),
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
        res = session.post(url=f'{URL}/api/student/add', data=json.dumps(data))
        status = json.loads(res.content)
        if status['status']:
            print (f'{i}: {status["data"]}')
        else:
            print(status['data'])
        time.sleep(WAIT_TIME)

populate_students(20)
