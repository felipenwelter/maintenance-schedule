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

#---------------------------------------------------------------
# Função: getIdle
# Parâmetros: list_so - list of service_orders
# Retorno: using list_os, fill all the blanks between tasks
#          with what is called idle schedules (list_idle)
#---------------------------------------------------------------
def getIdle(list_so):
    index = 0
    list_idle = []
    while index < len(list_so):
        if index == 0:
            list_idle.append({ 'employee': list_so[index]['employee'],
                               'start': start_date, 'end': list_so[index]['start'] })
        else:
            list_idle.append({ 'employee': list_so[index]['employee'],
                               'start': list_so[index-1]['end'], 'end': list_so[index]['start'] })
        index += 1

    # fill the last time with idle period, to show gantt
    if (list_so[-1]['end'] < end_date):
        list_idle.append({ 'employee': list_so[-1]['employee'],
                            'start': list_so[-1]['end'], 'end': end_date })

    return list_idle


#---------------------------------------------------------------
# Função: getUnavailable
# Parâmetros: list_idle - list of idle times
# Retorno: using list_idle, uses the employee shift to divide
#          what is really idle (based on work_shift) and what
#          is unavailability, the time off the schedule
#---------------------------------------------------------------
def getUnavailable(list_idle):

    # check if there are itens with different start/end day, then separate day by day
    index = 0
    while index < len(list_idle):
        if (list_idle[index]['start'][:10] != list_idle[index]['end'][:10]):

            end_day = datetime.datetime.strptime(list_idle[index]['start'], '%Y-%m-%d %H:%M').date()
            
            # fill all the days in the middle of the gap, if it has more than 2 days length
            while (end_day.strftime("%Y-%m-%d") != list_idle[index]['end'][:10]):
                end_day = end_day + datetime.timedelta(days=1)
                if (end_day.strftime("%Y-%m-%d") != list_idle[index]['end'][:10]):
                    list_idle.append({ 'employee': list_idle[index]['employee'],
                                'start': end_day.strftime("%Y-%m-%d")+" 00:00", 'end': end_day.strftime("%Y-%m-%d") + " 23:59" })

            list_idle.append({ 'employee': list_idle[index]['employee'],
                            'start': list_idle[index]['end'][:10]+" 00:00", 'end': list_idle[index]['end'] })
            list_idle[index]['end'] = list_idle[index]['start'][:10] + " 23:59"

        index += 1 

    # order by start date
    list_idle.sort(key=sortingRule)

    index = 0
    while index < len(list_idle):
        weekday = (datetime.datetime.strptime(list_idle[index]['start'], '%Y-%m-%d %H:%M')).weekday()
        shift = work_shift[0]['shift'][weekday]
        
        start = list_idle[index]['start'][11:]
        end = list_idle[index]['end'][11:]

        if len(shift) > 0:
            if (end >= shift[0] and end <= shift[1]):
                list_unavailable.append({ 'employee': list_idle[index]['employee'],
                                        'start': list_idle[index]['start'][:11] + start, 
                                        'end': list_idle[index]['end'][:11] + shift[0] })
                list_idle[index]['start'] = list_idle[index]['start'][:11] + shift[0]

            if (start >= shift[0] and start <= shift[1]):
                list_unavailable.append({ 'employee': list_idle[index]['employee'],
                                        'start': list_idle[index]['start'][:11] + shift[1], 
                                        'end': list_idle[index]['end'][:11] + end})
                list_idle[index]['end'] = list_idle[index]['end'][:11] + shift[1]

            if (start < shift[0] and end >= shift[1]):
                list_unavailable.append({ 'employee': list_idle[index]['employee'],
                                        'start': list_idle[index]['start'][:11] + "00:00", 
                                        'end': list_idle[index]['end'][:11] + shift[0]})
                list_unavailable.append({ 'employee': list_idle[index]['employee'],
                                        'start': list_idle[index]['start'][:11] + shift[1], 
                                        'end': list_idle[index]['end'][:11] + "23:59"})
                list_idle[index]['start'] = list_idle[index]['start'][:11] + shift[0]
                list_idle[index]['end'] = list_idle[index]['end'][:11] + shift[1]

        else: #if len(shift) == 0
            list_unavailable.append({ 'employee': list_idle[index]['employee'],
                                        'start': list_idle[index]['start'], 
                                        'end': list_idle[index]['end']})
            list_idle.pop(index)
            index -= 1


        index += 1

    # run the whole list_idle to get items to eliminate
    index = 0
    while index < len(list_idle):
        if (list_idle[index]['start'] == list_idle[index]['end']):
            list_idle.pop(index)
            index -= 1
        index += 1

    return list_unavailable





wl = jm.loadJSON()
df = []

#### TODO
# calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui

start_date = '2020-10-01 00:00'
end_date = ''
list_so = []
list_idle = []
list_unavailable = []
work_shift = [ { 'employee': 'Luiza',
                'shift': [['08:00','18:00'], ['08:00','18:00'], ['08:00','18:00'], ['09:00','14:00'], ['08:00','18:00'],'',''] }  ]

for so in wl['workload']:
    new = dict(Task=so['employee'], Start=so['start'],
               Finish=so['end'], Resource='busy')
    df.append(new)
    
    if (so['employee'] == 'Nelson'):
        list_so.append({ 'employee': so['employee'], 'start': so['start'], 'end': so['end'] })

# order the list by start date
list_so.sort(key=sortingRule)

#after getting all the service orders, update the last date to gantt
end_date = list_so[-1]['end'][:11]+"23:59"

# check if first value is lower then gantt start_date
if (list_so[0]['start'] < start_date):
    start_date = list_so[0]['start']

# get the gaps between service orders
list_idle = getIdle(list_so)

# extract the unavaiable periods into the idle periods identified previously
list_unavailable = getUnavailable(list_idle)


# add the idle into the gantt chart
for so in list_idle:
    new = dict(Task=so['employee'], Start=so['start'],
               Finish=so['end'], Resource='idle')
    df.append(new)

# add the unavailable into the gantt chart
for so in list_unavailable:
    new = dict(Task=so['employee'], Start=so['start'],
               Finish=so['end'], Resource='unavailable')
    df.append(new)

colors = {'busy': 'rgb(30,144,255)',
        'idle': 'rgb(230,90,90)',
        'unavailable': 'rgb(205,205,205)'}

fig = ff.create_gantt(df, colors=colors, index_col='Resource',
                    show_colorbar=True, group_tasks=True)
fig.show()


