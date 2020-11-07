# https://plotly.com/python/gantt/

# TODO
# calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui


import plotly.figure_factory as ff
import jsonManipulate as jm
import pandas as pd
import schedule

start_date = ''
end_date = ''

#---------------------------------------------------------------
# Function: showGantt
# Description: Display the gantt chart for the scheduled
#              service orders
#---------------------------------------------------------------
def showGantt(wl=[], ws=[]):
    
    global start_date, end_date

    # if do not receive a list of service_orders, load from json
    if len(wl) == 0:
        wl = jm.loadJSON_SO() #load list of service orders from JSON

    if len(ws) == 0:
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
        i['schedule'].sort(key=schedule.sortingRule)

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
                                'schedule': schedule.getSchedule(i['schedule'], schedule.getWorkShift(i['employee']),
                                start_date, end_date ) } ) 

    # add the whole schedule into the gantt chart
    for emp in full_schedule:
        for sc in emp['schedule']:
            for appt in sc['list']:
                day = sc['day'].strftime('%Y-%m-%d') + " "
                new = dict(Task=emp['employee'], Start=(day+appt['start']),
                        Finish=(day+appt['end']), Resource=appt['type'])
                gantt.append(new)

    colors = {'so': 'rgb(30,144,255)',
            'overtime': 'rgb(24,96,255)',
            'idle': 'rgb(230,90,90)',
            'unavailable': 'rgb(205,205,205)'}

    # shows the gantt chart on screen
    fig = ff.create_gantt(gantt, colors=colors, index_col='Resource',
                        show_colorbar=True, group_tasks=True)
    fig.show()


if __name__ == "__main__":
    showGantt()