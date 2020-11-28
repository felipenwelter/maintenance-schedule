# TODO - calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui

# Ref:
# https://plotly.com/python/gantt/

import plotly.figure_factory as ff
import jsonManipulate as jm
import pandas as pd
import schedule

start_date = ''
end_date = ''

#---------------------------------------------------------------
# Function ShowGantt: 
#     Show a gantt chart with the periods of each task
#     scheduled for each employee
# Parameters
#    wl - work list, optional (load default)
#    ws - work shift, optional (load default)
#---------------------------------------------------------------
def showGantt(wl=[], ws=[]):
    
    global start_date, end_date

    # if do not receive a list of tasks, load example from json
    if len(wl) == 0:
        wl = jm.loadJSON_tasks() #load list of tasks from JSON

    if len(ws) == 0:
        work_shift = jm.loadJSON_ws() #load list of work shifts from JSON

    #initialize global variables
    start_date = ''
    end_date = ''
    gantt = []
    list_tasks = []
    full_schedule = []

    # aggregate tasks by employee
    for task in wl['workload']:
        idx = -1
        i = 0
        
        while i < len(list_tasks):
            if (list_tasks[i]['employee'] == task['employee']):
                idx = i
            i += 1
        
        if (idx < 0):
            list_tasks.append( { 'employee': task['employee'], 'schedule': [] } )
            list_tasks[-1]['schedule'].append( {'start': task['start'], 'end': task['end']} )
        else:
            list_tasks[idx]['schedule'].append( {'start': task['start'], 'end': task['end']} )


    # order each list of tasks by start date
    for i in list_tasks:
        i['schedule'].sort(key=schedule.sortingRule)

    # identifies the first and last date at all
    for i in list_tasks:
        if ( start_date == '' or i['schedule'][0]['start'] < start_date):
            start_date = i['schedule'][0]['start']
        if ( end_date == '' or i['schedule'][-1]['end'] > end_date):
            end_date = i['schedule'][-1]['end']

    start_date = start_date[:11]+"00:00"
    end_date = end_date[:11]+"23:59"

    # get full schedule (with busy, idle and unavailable time)
    for i in list_tasks:
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

    colors = {'busy': 'rgb(30,144,255)',
            'overtime': 'rgb(24,96,255)',
            'idle': 'rgb(230,90,90)',
            'unavailable': 'rgb(205,205,205)'}

    # shows the gantt chart on screen
    fig = ff.create_gantt(gantt, colors=colors, index_col='Resource',
                        show_colorbar=True, group_tasks=True)
    fig.show()


if __name__ == "__main__":
    showGantt()