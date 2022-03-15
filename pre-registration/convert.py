import json, re, csv, datetime

convert_parent_name = False
convert_child_name = True

def convert_name(keys, line):
    stop = False
    first_name_key = keys['first_name']
    last_name_key = keys['last_name']
    full_name_key = keys['full_name']
    if first_name_key not in line or  last_name_key not in line or line[first_name_key] == ""  and line[last_name_key] == "":
        names = re.sub(' +', ' ', line[full_name_key].strip()).split(' ')
        names2 = []
        for i, n in enumerate(names):
            names2.append(str(i))
            names2.append(n)
        full_name = ' '.join(names2[1:])
        res = input(f'<s>x<r>: {full_name}  ?')
        if res != '':
            if res[0] == 's':
                stop = True
            else:
                full_name = line[full_name_key]
                pos = int(res[0])
                reverse = len(res) > 1 and res[1] == 'r'
                names = full_name.split(' ')
                first_name = ' '.join(names[:pos])
                last_name = ' '.join(names[pos:])
                line[first_name_key] = first_name if not reverse else last_name
                line[last_name_key] = last_name if not reverse else first_name
                print(line[first_name_key], line[last_name_key], line[full_name_key])
    return line, stop


def convert_input_json():
    stop = False
    out_json = []
    with open('out.json', "w") as out_file:
        with open('in.json') as in_file:
            in_json = json.load(in_file)
            for l in in_json:
                if not stop:
                    if convert_parent_name:
                        l, stop = convert_name({'first_name': 'first_name', 'last_name': 'last_name', 'full_name': 'full_name'}, l)
                    if convert_child_name:
                        l, stop = convert_name({'first_name': 'child_first_name', 'last_name': 'child_last_name', 'full_name': 'child_name'}, l)
                out_json.append(l)
            json.dump(out_json, out_file)

# convert_input_json()

c_register = 1
c_indicator = 2
c_register_number = 3
c_register_date = 4
c_last_name = 5
c_first_name = 6
c_brister = 7
c_sex = 9
c_klassieke_talen = 15
c_stem = 16
c_moderne_talen = 17
c_sport = 18
c_bedrijf = 19
c_maatschappij = 20
c_finse = 21
c_cultuur = 22
c_1b = 23
c_doubt = 24
c_note = 28

colmun_to_field_of_study = {
    15: '1a SUL-klassieke-talen',
    16: '1a SUL-stem',
    17: '1a SUL-moderneTalenEnWetenschappen',
    18: '1a SUL-sport-en-wetenschappen',
    19: '1a SUI-bedrijfEnOrganisatie',
    20: '1a SUI-maatschappijEnWelzijn',
    21: '1a SUI-finseCademie',
    22: '1a SUI-cultuurEnMedia',
    23: '1b-1B',
}

colmun_to_register = {
    15: 'SUL',
    16: 'SUL',
    17: 'SUL',
    18: 'SUL',
    19: 'SUI',
    20: 'SUI',
    21: 'SUI',
    22: 'SUI',
    23: 'BSUI',
}

second_offset = 0
def get_timestamp(row):
    global second_offset
    register_nbr = int(row[c_register_number][-2:])
    date_in = row[c_register_date]
    register_timestamp = datetime.datetime.strptime(date_in, '%d/%m/%Y')
    register_timestamp += datetime.timedelta(seconds=register_nbr)
    second_offset += 1
    return register_timestamp.strftime('%Y-%m-%dT%H:%M:%S')


def get_field_of_study(row):
    for i in range(c_klassieke_talen, c_1b + 1):
        if row[i] == '1':
            return colmun_to_field_of_study[i]
        if row[i] == '?' and row[c_register] == colmun_to_register[i]:
            return colmun_to_field_of_study[i]

def process_pre_registration_csv():
    out = []
    timeslot_cache = {}
    with open('out.json') as timeslot_in_file:
        registered_with_timeslots = json.load(timeslot_in_file)
        for l in registered_with_timeslots:
            timeslot_cache[l['child_name']] = l
        with open('pre-reg-out.json', "w") as out_file:
            with open('pre-reg-in.csv', newline='') as csvfile:
                pre_registrations = csv.reader(csvfile, delimiter=';')
                for i, row in enumerate(pre_registrations):
                    field_of_study = get_field_of_study(row)
                    register_timestamp = get_timestamp(row)
                    guest = {
                        'field_of_study': field_of_study,
                        'indicator': row[c_indicator] == 'I',
                        'register_timestamp': register_timestamp,
                        'child_last_name': row[c_last_name],
                        'child_first_name': row[c_first_name],
                        'reason_priority': f'brus: {row[c_brister]}',
                        'sex': row[c_sex],
                        'note': row[c_note],
                        'pre_register': True
                    }
                    for i, l in enumerate(registered_with_timeslots):
                        if row[c_last_name].lower().strip() in l['child_name'].lower() and row[c_first_name].lower().strip() in l['child_name'].lower():
                            guest.update({
                                'email': l['email'],
                                'phone': l['phone'],
                                'first_name': l['first_name'],
                                'last_name': l['last_name'],
                                'code': l['code'],
                                'timeslot': l['timeslot'].replace(' ', 'T')
                            })
                            del registered_with_timeslots[i]
                            break
                    print(guest)
                    out.append(guest)
            out_string = json.dumps(out)
            out_string = re.sub('},', '},\n', out_string)
            # json.dump(out, out_file)
            out_file.write(out_string)
            print('Remainging in timeslot registrations:')
            for i in registered_with_timeslots:
                print (i['email'], i['last_name'], i['first_name'])

process_pre_registration_csv()
