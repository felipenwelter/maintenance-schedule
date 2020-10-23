import json

def loadJSON_SO():

    data = {}
    data['workload'] = []

    with open('entry-gantt.json') as json_file:
        source = json.load(json_file)
        for p in source['workload']:
            data['workload'].append({
                'number': p['number'],
                'start': p['start'],
                'end': p['end'],
                'employee': p['employee']
            })
    return data

def loadJSON_WS():

    data = {}
    data['workshift'] = []
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    with open('entry-work-shift.json') as json_file:
        
        source = json.load(json_file)
        
        for p in source['workshift']:
            details = []
            
            for d in days:
                details.append([])
                matches = [x for x in p['shift'] if x['day'] == d]
                for m in matches:
                    details[-1].append( [ m['start'], m['end'] ] )
            
            data['workshift'].append( {'employee': p['employee'], 'shift': details } )

    return data