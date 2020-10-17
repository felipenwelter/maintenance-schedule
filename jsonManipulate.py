import json

def loadJSON():

    data = {}
    data['workload'] = []

    with open('entry.json') as json_file:
        source = json.load(json_file)
        for p in source['workload']:
            data['workload'].append({
                'number': p['number'],
                'start': p['start'],
                'end': p['end'],
                'employee': p['employee']
            })
    return data