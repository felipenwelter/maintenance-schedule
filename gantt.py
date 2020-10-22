# https://plotly.com/python/gantt/

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
# Função: getSchedule
# Parâmetros: list_so - list of service_orders
# Retorno: using list_os, fill all the blanks between tasks
#          with what is called idle schedules and also with 
#          the unavailable periods (off schedule)
#---------------------------------------------------------------
def getSchedule(list_so):

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
        shift = work_shift[0]['shift'][weekday]

        if (shift[0] != ''):

            for sc in shift:
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

#### TODO
#OK teste OS comecando antes do turno da tarde e acabando antes              x-x[      ]
#OK 11:00 - 12:50 / 12:10 - 12:50
#OK teste OS comecando antes do turno da tarde e acabando dentro              x-[----x-]
#OK 11:00 - 14:00 / 12:10 - 14:00
#OK teste OS comecando antes do turno da tarde e acabando fora                x-[------]-x
#OK 11:00 - 19:00 / 12:10 - 19:00
#OK teste OS comecando exatamente no turno da tarde e acabando dentro           x---x  ]
#OK 13:00 - 15:00
#OK teste OS comecando exatamente no turno da tarde e acabando fora             x------]-x
#OK 13:00 - 19:00
#OK teste OS comecando dentro do turno da tarde e acabando dentro               [ x--x ]
#OK 14:00 - 15:00
#OK teste OS comecando dentro do turno da tarde e acabando fora                 [ x----]-x
#OK 14:00 - 19:00
#OK teste OS comecando exatamente no fim do turno da tarde e acabando fora      [      x-x
#OK 18:00 - 19:00
#teste OS comecando depois do turno da tarde e acabando depois               [      ] x-x
#20:00 - 21:00

#OK teste OS comecando antes do turno da manha e acabando antes              x-x[      ]
#OK 06:00 - 07:00 
#OK teste OS comecando antes do turno da manha e acabando dentro              x-[----x-]
#OK 06:00 - 09:00
#OK teste OS comecando antes do turno da manha e acabando fora                x-[------]-x
#OK 06:00 - 12:30
#OK teste OS comecando exatamente no turno da manha e acabando dentro           x---x  ]
#OK 08:00 - 10:00
#OK teste OS comecando exatamente no turno da manha e acabando fora             x------]-x
#OK 08:00 - 12:30
#OK teste OS comecando dentro do turno da manha e acabando dentro               [ x--x ]
#OK 09:00 - 10:00
#OK teste OS comecando dentro do turno da manha e acabando fora                 [ x----]-x
#OK 09:00 - 12:30
#OK teste OS comecando exatamente no fim do turno da manha e acabando fora      [      x-x
#OK 12:00 - 12:30
#OK teste OS comecando depois do turno da manha e acabando depois               [      ] x-x
#OK 12:10 - 12:50






wl = jm.loadJSON()
df = []



# TODO
# calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui
# poder incluir agenda de varias pessoas ao mesmo tempo no gantt
# poder usar o calendario individual e cada um (json)

start_date = '2020-10-01 00:00'
end_date = ''
list_so = []
list_idle = []
list_unavailable = []
work_shift = [ { 'employee': 'Nelson',
                'shift': [
                    [ ['08:00','12:00'], ['13:00','18:00'] ], #monday
                    [ ['08:00','12:00'], ['13:00','18:00'] ], #tuesday
                    [ ['08:00','12:00'], ['13:00','18:00'] ], #wednesday
                    [ ['08:00','12:00'], ['13:00','18:00'] ], #thursday
                    [ ['08:00','12:00'], ['13:00','18:00'] ], #friday
                    [ '' ], #saturday
                    [ '' ]  #sunday
                ] }  ]

for so in wl['workload']:
    #new = dict(Task=so['employee'], Start=so['start'],
    #           Finish=so['end'], Resource='busy')
    #df.append(new)
    if (so['employee'] == 'Nelson'):
        list_so.append({ 'employee': so['employee'], 'start': so['start'], 'end': so['end'] })

# order the list by start date
list_so.sort(key=sortingRule)

#after getting all the service orders, update the last date to gantt
end_date = list_so[-1]['end'][:11]+"23:59"

# check if first value is lower then gantt start_date
if (list_so[0]['start'] < start_date):
    start_date = list_so[0]['start']

# get full schedule
full_schedule = getSchedule(list_so)

# add the idle into the gantt chart
for sc in full_schedule:
    for appt in sc['list']:
        day = sc['day'].strftime('%Y-%m-%d') + " "
        new = dict(Task='Nelson', Start=(day+appt['start']),
                Finish=(day+appt['end']), Resource=appt['type'])
        df.append(new)

colors = {'so': 'rgb(30,144,255)',
          'idle': 'rgb(230,90,90)',
          'unavailable': 'rgb(205,205,205)'}

fig = ff.create_gantt(df, colors=colors, index_col='Resource',
                    show_colorbar=True, group_tasks=True)
fig.show()


