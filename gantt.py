# https://plotly.com/python/gantt/

import plotly.figure_factory as ff
import jsonManipulate as jm
import pandas as pd

import datetime



def myFunc(e):
  return e['start']



print( jm.loadJSON()['workload'][0]['employee'] )

wl = jm.loadJSON()

df = []
#[[dict(Task="Nelson", Start='2020-01-01 10:00', Finish='2020-02-02 03:00', Resource='009372'),
#      dict(Task="Nelson", Start='2020-02-15', Finish='2020-03-15', Resource='003711'),
#      dict(Task="Mauricio", Start='2020-01-01', Finish='2020-02-02 11:00', Resource='000881'),
#      dict(Task="Luiza", Start='2020-03-10', Finish='2020-03-20', Resource='009372'),
#      dict(Task="Luiza", Start='2020-04-01', Finish='2020-04-20', Resource='034830'),
#      dict(Task="Luiza", Start='2020-05-18', Finish='2020-06-18', Resource='000881'),
#      dict(Task="Antonio", Start='2020-01-14', Finish='2020-03-14', Resource='003711')]
#]
#df2 = dict(Task=wl['workload'][0]['employee'], Start=wl['workload'][0]['start'],
#           Finish=wl['workload'][0]['end'], Resource=wl['workload'][0]['number'])
#df.append(df2)

#### TODO
# check if it is possible to show the time as hint
# use colors to identify: green - allocated; gray - unavaiable, red - idle
# calcular qual a ociosidade geral e por funcionario no comeco e depois no final, pra ver se aumenta ou diminui

start_date = '2020-10-01 00:00'
list_so = []
list_gaps = []
work_shift = [ { 'employee': 'Luiza',
                 'shift_start': ['08:00','08:00','08:00','08:00','08:00','',''],
                 'shift_end': ['18:00','18:00','18:00','18:00','18:00','',''] }  ]

for so in wl['workload']:
    new = dict(Task=so['employee'], Start=so['start'],
            Finish=so['end'], Resource='busy') #Resource=so['number'])
    df.append(new)
    
    if (so['employee'] == 'Luiza'):
        list_so.append({ 'employee': so['employee'], 'start': so['start'], 'end': so['end'] })

# order the list by start date
list_so.sort(key=myFunc)

# check if first value is lower then gantt start_date
if (list_so[0]['start'] < start_date):
    start_date = list_so[0]['start']

# get the gaps between service orders
index = 0
while index < len(list_so):
    if index == 0:
        list_gaps.append({ 'employee': list_so[index]['employee'],
                           'start': start_date, 'end': list_so[index]['start'] })
    else:
        list_gaps.append({ 'employee': list_so[index]['employee'],
                           'start': list_so[index-1]['end'], 'end': list_so[index]['start'] })
    index += 1

# extract the unavaiable periods into the idle periods identified previously
#index = 0
#while index > len(list_gaps):
#    weekday = (datetime.datetime.strptime(list_gaps[0]['start'], '%Y-%m-%d %H:%M')).weekday()
    
    #list_gaps[index]['start']
    #work_shift[0]['shift_start'][weekday]
        
    

    


# add the gaps into the gantt chart
for so in list_gaps:
    new = dict(Task=so['employee'], Start=so['start'],
            Finish=so['end'], Resource='idle') #Resource=so['number'])
    df.append(new)


#colors = {'000881': 'rgb(220, 0, 0)',
#          '009372': (1, 0.9, 0.16),
#          '003711': (0.1, 0.1, 0.9),
#          '034830': 'rgb(100, 255, 100)'}

colors = {'busy': 'rgb(30,144,255)',
          'idle': 'rgb(178,34,34)',
          'unavaiable': 'rgb(176,196,222)'}

fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True,
                      group_tasks=True)
fig.show()