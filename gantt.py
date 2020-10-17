# https://plotly.com/python/gantt/

import plotly.figure_factory as ff
import jsonManipulate as jm
import pandas as pd

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


for so in wl['workload']:
    new = dict(Task=so['employee'], Start=so['start'],
            Finish=so['end'], Resource='busy') #Resource=so['number'])
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