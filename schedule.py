import datetime
import jsonManipulate as jm

#---------------------------------------------------------------
# Função: sortingRule
# Parâmetros: e - the item of the list
# Retorno: defines the sorting rule of list_os
#---------------------------------------------------------------
def sortingRule(e):
  return e['start']


#--------------------------------------------------------------------
# Função: checkPeriods
# Parâmetros: ds - daily schedule, with so, idle and unavailable time
# Retorno: null
#--------------------------------------------------------------------
def checkPeriods(ds):

    if len(ds) == 0:
        print("ERRO - NENHUM PERIODO PARA O DIA")

    if ds[0]['start'] != "00:00":
        print("ERRO - PERIODO NAO COMECA AS 00:00")

    if ds[-1]['end'] != "23:59":
        print("ERRO - PERIODO NAO TERMINA AS 23:59")

    idx = 0
    while (idx < len(ds)):
        if (idx < (len(ds)-1) and ds[idx]['end'] != ds[idx+1]['start']):
            print("ERRO - PERIODO NAO COMECA NO TERMINO DO ANTERIOR -",ds[idx]['end'],ds[idx+1]['start'])
        idx += 1
        

#---------------------------------------------------------------
# Function: getWorkShift
# Parâmetros: employee - name of the employee
# Retorno: using the imported work_shift json file, find the one
# #        corresponding to the name of the employee
#---------------------------------------------------------------
def getWorkShift(employee):

    work_shift = jm.loadJSON_ws() #load list of work shifts from JSON

    ret = []
    for ws in work_shift['workshift']:
        if (ws['employee'] == employee):
            ret = ws['shift']
            break
    
    return ret


#---------------------------------------------------------------
# Função: getSchedule
# Parâmetros: list_tasks - list of tasks
#             list_ws - list of the work_shift
#             start_date - global start date (for all S.O. of all employees)
#             end_date - global end date (for all S.O. of all employees)
# Retorno: using list_os, fill all the blanks between tasks
#          with what is called idle schedules and also with 
#          the unavailable periods (off schedule)
#---------------------------------------------------------------
def getSchedule(list_tasks, list_ws, start_date, end_date):
    
    #overflow = False
    full_periods = []
    dt = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').date()
    dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').date()

    while (dt <= dt_end): # or overflow:
        
        ds = [] #day_schedule
        weekday = dt.weekday()

        for task in list_tasks:

            # first of all, aggregate only the same day infos
            if datetime.datetime.strptime(task['start'], '%Y-%m-%d %H:%M').date() == dt:

                # check if starts and ends in the same day, if not, get only this day info
                if (task['end'][:10] == task['start'][:10]):
                    ds.append({ 'start': task['start'][-5:],
                                'end': task['end'][-5:],
                                'type': 'busy' })
                else:
                    ds.append({ 'start': task['start'][-5:],
                                'end': "23:59",
                                'type': 'busy' })

            elif datetime.datetime.strptime(task['end'], '%Y-%m-%d %H:%M').date() == dt:

                # check if starts and ends in the same day, if not, get only this day info
                if (task['start'][:10] == task['end'][:10]):
                    ds.append({ 'start': task['start'][-5:],
                                'end': task['end'][-5:],
                                'type': 'busy' })
                else:
                    ds.append({ 'start': "00:00",
                                'end': task['end'][-5:],
                                'type': 'busy' })

            # and if it is the last day, check if there is overflow
            #if (dt == dt_end) and (datetime.datetime.strptime(task['end'], '%Y-%m-%d %H:%M').date() > dt_end):
            #    overFlow = True

        # when there is any task that finishes at 00:00
        # then it will be included a period with same start and end
        # so, the next step removes this invalid periods
        # ex: {'end': '2020-11-17 00:00', 'start': '2020-11-16 21:00'}
        # would generate 2020-11-17 00:00 to 2020-11-17 00:00
        # obs: not expecting that the task must be adjusted before
        i = 0
        while i < len(ds):
            if ds[i]['start'] == ds[i]['end']:
                ds.pop(i)
                i = i-1
            i += 1

        # identify the overtime periods and split them from the s.o.
        for task in ds:

            # so, first split all the s.o's that cross any shift start or end
            for sc in list_ws[weekday]:
                
                if sc[0] > task['start'] and sc[0] < task['end']:
                    ds.append({ 'start': sc[0],
                                'end': task['end'],
                                'type': 'busy' })
                    task['end'] = sc[0]

                if sc[1] > task['start'] and sc[1] < task['end']:
                    ds.append({ 'start': sc[1],
                                'end': task['end'],
                                'type': 'busy' })
                    task['end'] = sc[1]

        # second, label correctly each period
        for task in ds:
            
            inshift = 0
            for sc in list_ws[weekday]:
                if (task['start'] >= sc[0] and task['end'] <= sc[1]):
                    inshift += 1
            
            if (inshift == 0):
                task['type'] = 'overtime'


        # now join with the schedule info
        if list_ws[weekday]:
            for sc in list_ws[weekday]:
                ds.append({ 'start': sc[0],
                            'end': sc[1],
                            'type': 'idle' })


            # then detect the idle periods
            ds.sort(key=sortingRule)
            idx = 0

            while idx < len(ds):
                
                if ds[idx]['type']  == 'idle':
                    
                    if idx < (len(ds)-1) and (ds[idx]['end'] > ds[idx+1]['start']): #if end >= than next period start

                        if (ds[idx]['end'] > ds[idx+1]['end']): #check if needs to split

                            ds.append({ 'start': ds[idx+1]['end'],
                                        'end': ds[idx]['end'],
                                        'type': ds[idx]['type'] })
                            ds[idx]['end'] = ds[idx+1]['start'] #reduce using the next start as the end
                            ds.sort(key=sortingRule)
                            idx = 0
                            continue #restart the while loop

                        ds[idx]['end'] = ds[idx+1]['start'] #reduce using the next start as the end
                    
                    if idx > 0 and ds[idx]['start'] < ds[idx-1]['end']:
                        ds[idx]['start'] = ds[idx-1]['end'] #reduce using the previous end as the start

                    #if the period became inverted or zero-length, remove it
                    if ds[idx]['start'] >= ds[idx]['end']:
                        ds.pop(idx)
                        idx -= 1
                
                idx += 1

        
        # and finally, detect the unavailable periods (off schedule)
        idx = 0
        limit = len(ds)
        ds.sort(key=sortingRule)

        if limit == 0:
            ds.append({ 'start': "00:00",
                        'end': "23:59",
                        'type': 'unavailable'})
        else:
            while idx < limit:
                
                # if the first item isn't day start (00:00)
                if (idx == 0 and ds[idx]['start'] != "00:00"):
                    ds.append({ 'start': "00:00",
                                'end': ds[idx]['start'],
                                'type': 'unavailable' })

                if idx < (limit-1) and (ds[idx]['end'] != ds[idx+1]['start']): #if there is a gap between periods
                    ds.append({ 'start': ds[idx]['end'],
                                'end': ds[idx+1]['start'],
                                'type': 'unavailable' })

                if (idx == (limit-1) and ds[idx]['end'] != "23:59"):
                    ds.append({ 'start': ds[idx]['end'],
                                'end': "23:59",
                                'type': 'unavailable' })
                
                idx += 1


        ds.sort(key=sortingRule)
        checkPeriods(ds)  # only development

        full_periods.append({ 'day': dt, 'list': ds })

        dt = dt + datetime.timedelta(days=1)    

    return full_periods