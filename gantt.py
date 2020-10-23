# https://plotly.com/python/gantt/

# TODO
# calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui


import plotly.figure_factory as ff
import jsonManipulate as jm
import pandas as pd
import datetime


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
            print("ERRO - PERIODO NAO COMECA NO TERMINO DO ANTERIOR")
        idx += 1
        

#---------------------------------------------------------------
# Função: getWorkShift
# Parâmetros: employee - name of the employee
# Retorno: using the imported work_shift json file, find the one
# #        corresponding to the name of the employee
#---------------------------------------------------------------
def getWorkShift(employee):
    ret = []
    for ws in work_shift['workshift']:
        if (ws['employee'] == employee):
            ret = ws['shift']
            break
    return ret


#---------------------------------------------------------------
# Função: getSchedule
# Parâmetros: list_so - list of service_orders
#             list_ws - list of the work_shift
# Retorno: using list_os, fill all the blanks between tasks
#          with what is called idle schedules and also with 
#          the unavailable periods (off schedule)
#---------------------------------------------------------------
def getSchedule(list_so, list_ws):

    full_periods = []
    dt = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').date()
    dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').date()

    while (dt <= dt_end):
        
        ds = [] #day_schedule

        for so in list_so:

            # first of all, aggregate only the same day infos
            if datetime.datetime.strptime(so['start'], '%Y-%m-%d %H:%M').date() == dt:

                # check if starts and ends in the same day, if not, get only this day info
                if (so['end'][:10] == so['start'][:10]):
                    ds.append({ 'start': so['start'][-5:],
                                'end': so['end'][-5:],
                                'type': 'so' })
                else:
                    ds.append({ 'start': so['start'][-5:],
                                'end': "23:59",
                                'type': 'so' })

            elif datetime.datetime.strptime(so['end'], '%Y-%m-%d %H:%M').date() == dt:

                # check if starts and ends in the same day, if not, get only this day info
                if (so['start'][:10] == so['end'][:10]):
                    ds.append({ 'start': so['start'][-5:],
                                'end': so['end'][-5:],
                                'type': 'so' })
                else:
                    ds.append({ 'start': "00:00",
                                'end': so['end'][-5:],
                                'type': 'so' })

        
        # now join with the schedule info
        weekday = dt.weekday()
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




wl = jm.loadJSON_SO() #load list of service orders from JSON
work_shift = jm.loadJSON_WS() #load list of work shifts from JSON

#initialize global variables
start_date = ''
end_date = ''
gantt = []
list_so = []
full_schedule = []

# aggregate service orders by employee
for so in wl['workload']:
    idx = -1
    i = 0
    
    while i < len(list_so):
        if (list_so[i]['employee'] == so['employee']):
            idx = i
        i += 1
    
    if (idx < 0):
        list_so.append( { 'employee': so['employee'], 'schedule': [] } )
        list_so[-1]['schedule'].append( {'start': so['start'], 'end': so['end']} )
    else:
        list_so[idx]['schedule'].append( {'start': so['start'], 'end': so['end']} )


# order each list of service_orders by start date
for i in list_so:
    i['schedule'].sort(key=sortingRule)

# identifies the first and last date at all
for i in list_so:
    if ( start_date == '' or i['schedule'][0]['start'] < start_date):
        start_date = i['schedule'][0]['start']
    if ( end_date == '' or i['schedule'][-1]['end'] > end_date):
        end_date = i['schedule'][-1]['end']

start_date = start_date[:11]+"00:00"
end_date = end_date[:11]+"23:59"

# get full schedule (with busy, idle and unavailable time)
for i in list_so:
    full_schedule.append( { 'employee': i['employee'],
                            'schedule': getSchedule(i['schedule'], getWorkShift(i['employee']) ) } ) 

# add the whole schedule into the gantt chart
for emp in full_schedule:
    for sc in emp['schedule']:
        for appt in sc['list']:
            day = sc['day'].strftime('%Y-%m-%d') + " "
            new = dict(Task=emp['employee'], Start=(day+appt['start']),
                    Finish=(day+appt['end']), Resource=appt['type'])
            gantt.append(new)

colors = {'so': 'rgb(30,144,255)',
          'idle': 'rgb(230,90,90)',
          'unavailable': 'rgb(205,205,205)'}

# shows the gantt chart on screen
fig = ff.create_gantt(gantt, colors=colors, index_col='Resource',
                    show_colorbar=True, group_tasks=True)
fig.show()
