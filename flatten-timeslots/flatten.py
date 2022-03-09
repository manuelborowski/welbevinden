import json, datetime

out_json = []
with open('in.json') as in_file:
    in_json = json.load(in_file)
    print (in_json)
    for t in in_json:
        start_time = datetime.datetime(t['year'], t['month'], t['day'], t['hour'], t['minute'])
        length = t['length']
        number = t['number']
        places = t['places']
        print(start_time, length, number, places)
        for i in range(number):
            time = start_time + datetime.timedelta(minutes=(length * i))
            out_json.append({
                'year': time.year,
                'month': time.month,
                'day': time.day,
                'hour': time.hour,
                'minute': time.minute,
                'length': length,
                'number': 1,
                'places': places
            })
    print (out_json)
    with open('out.json', "w") as out_file:
        json.dump(out_json, out_file)