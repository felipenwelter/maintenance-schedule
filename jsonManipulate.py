import json

#---------------------------------------------------------------
# Function loadJSON_tasks: 
#    Load json file with tasks/service order information
#---------------------------------------------------------------
def loadJSON_tasks():

    data = {}
    data['workload'] = []

    with open('datasets/entry-gantt.json') as json_file:
        source = json.load(json_file)
        for p in source['workload']:
            data['workload'].append({
                'number': p['number'],
                'start': p['start'],
                'end': p['end'],
                'employee': p['employee']
            })
    return data

#---------------------------------------------------------------
# Function loadJSON_employee_ws: 
#    Load json file with workshift information (daily periods of 
#    availability for each employee)
#---------------------------------------------------------------
def loadJSON_employee_ws():

    data = {}
    data['workshift'] = []
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    with open('datasets/entry-work-shift.json') as json_file:
        
        source = json.load(json_file)
        
        for p in source['workshift']:
            details = []
            
            for d in days:
                details.append([])
                matches = [x for x in p['shift'] if x['day'] == d]
                for m in matches:
                    details[-1].append( [ m['start'], m['end'] ] )
                
                #sort by start hour
                details[-1].sort()

            data['workshift'].append( {'employee': p['employee'], 'shift': details } )

    return data


#---------------------------------------------------------------
# Function loadJSON_equipment_ws: 
#    Load json file with workshift information (daily periods of 
#    operation for each equipment)
#---------------------------------------------------------------
def loadJSON_equipment_ws():

    data = {}
    data['workshift'] = []
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    with open('datasets/equipment-workshift.json') as json_file:
        
        source = json.load(json_file)
        
        for p in source['workshift']:
            details = []
            
            for d in days:
                details.append([])
                matches = [x for x in p['shift'] if x['day'] == d]
                for m in matches:
                    details[-1].append( [ m['start'], m['end'] ] )
                
                #sort by start hour
                details[-1].sort()

            data['workshift'].append( {'equipment': p['equipment'], 'shift': details } )

    return data