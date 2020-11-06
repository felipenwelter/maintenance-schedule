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
#             list_ws - list of the work_shift
#             start_date - global start date (for all S.O. of all employees)
#             end_date - global end date (for all S.O. of all employees)
# Retorno: using list_os, fill all the blanks between tasks
#          with what is called idle schedules and also with 
#          the unavailable periods (off schedule)
#---------------------------------------------------------------
def getSchedule(list_so, list_ws, start_date, end_date):
    
    full_periods = []
    dt = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').date()
    dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').date()

    while (dt <= dt_end):
        
        ds = [] #day_schedule
        weekday = dt.weekday()

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


        # identify the overtime periods and split them from the s.o.
        for so in ds:

            # so, first split all the s.o's that cross any shift start or end
            for sc in list_ws[weekday]:
                
                if sc[0] > so['start'] and sc[0] < so['end']:
                    ds.append({ 'start': sc[0],
                                'end': so['end'],
                                'type': 'so' })
                    so['end'] = sc[0]

                if sc[1] > so['start'] and sc[1] < so['end']:
                    ds.append({ 'start': sc[1],
                                'end': so['end'],
                                'type': 'so' })
                    so['end'] = sc[1]

        # second, label correctly each period
        for so in ds:
            
            inshift = 0
            for sc in list_ws[weekday]:
                if (so['start'] >= sc[0] and so['end'] <= sc[1]):
                    inshift += 1
            
            if (inshift == 0):
                so['type'] = 'overtime'


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