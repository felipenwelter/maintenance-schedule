import random
import config
import json
from datetime import datetime, timedelta
import schedule
import copy

#---------------------------------------------------------------
# Function search:
#    Search a value in a list and return the index
# Parameters:
#    list - list of single itens
#    value - value to compare
#---------------------------------------------------------------
def search(list,value):
    try:
        return list.index(value)
    except ValueError:
        return -1

#---------------------------------------------------------------
# Function sortingRule:
#    Function with a key to sort a list, by start date
# Parameters:
#    e - item of the list (sent by .sort())
#---------------------------------------------------------------
def sortingRule(e):
  return e['start']

#---------------------------------------------------------------
# Function getEmployeeHourlyWage:
#    Return the hourly wage of an employee
# Parameters:
#    cr - chromosome
#    e - name of employee
#---------------------------------------------------------------
def getEmployeeHourlyWage(cr,e):
    hourly_wage = 999
    for emp in cr.pop.ga.entry['employees']:
        if (emp['name'] == e):
            hourly_wage = float(emp['hourly-wage'])
            break
    return hourly_wage

#---------------------------------------------------------------
# Function getEquipmentHourlyCost:
#    Return the hourly cost of an stopped equipment
# Parameters:
#    cr - chromosome
#    e - name of equipment
#---------------------------------------------------------------
def getEquipmentHourlyCost(cr,e):
    hourly_cost = 999
    for eqp in cr.pop.ga.entry['equipments']:
        if (eqp['name'] == e):
            hourly_cost = float(eqp['hourly-cost'])
            break
    return hourly_cost


#---------------------------------------------------------------
# Class Chromosome: definitions of a chromosome, and individual
#   that represents a solution of the problem
#---------------------------------------------------------------
class Chromosome:
    '''Represents the invididuals and their characteristics'''

    def __init__(self,pop):

        self.pop = pop # class population of the chromosome (to access parameters)
        self.length = pop.chromosome_length # the chromosome lenght is calculated once in the population
        self.genes = [0 for i in range(self.length)] # initialize all genes as 0
        self.limits = pop.chromosome_limits  # defined by number ofdays and number of time blocks
        self.fitness = 0 # acceptance criteria

        self.employeeCost = 0
        self.equipmentCost = 0

        # deep copy of the task list
        self.task_list = []
        for li in self.pop.task_list:
            d2 = copy.deepcopy(li)
            self.task_list.append(d2)

        
    def initialize(self):
        '''Define 0s and 1s randomly to compose the chromosome'''
        for i in range(self.length):
            if divmod(i,2)[1] == 0:
                self.genes[i] = random.randint(0, self.limits[0])
            else:
                self.genes[i] = random.randint(0, self.limits[1])

        self.update() # update task list and calc fitness


    def update(self):
        '''Update the chromosome info using the genes definitions'''
        self.updateTaskList() # update the task list using genes information
        self.calcFitness() # calculate fitness of each individual


    def updateTaskList(self):
        '''Convert the genes into readable day-time info
           and save the updated task list into the chromosome'''
        count = 0
        list_tasks = []
        list_dates = []
        for so in self.pop.ga.entry['tasks']: # map genes to original tasks
            obj = self.genes[ (count*2) : (count*2)+2 ]

            task_day = obj[0] # get the day gene
            task_time = obj[1] # get the time block gene

            start = self.pop.start_date + timedelta(days=task_day)
            start += timedelta(minutes=(task_time * config.block_size))
            end = start + timedelta(hours=so['duration'])

            list_tasks.append(so['number'])
            list_dates.append([ start.strftime("%Y-%m-%d %H:%M"),
                                end.strftime("%Y-%m-%d %H:%M") ])
            count += 1

        # then use the saved arrays to append the start/end infos
        for so in self.task_list:
            idx = search(list_tasks, so['number'])
            so['start'] = list_dates[idx][0]
            so['end'] = list_dates[idx][1]


    def calcFitness(self):
        '''Check constraints and update the fitness value'''
        
        # reset fitness value
        self.fitness = 0

        # check hard constraints, the ones that invalidate the chromosome
        self.checkHardConstraints()

        # continue checking the soft constraints only if passed through hard constraints
        if (self.fitness < 0):
            return

        # if consider Employee Wage to calc fitness
        if (config.useEmployeeWage == True):
            # the soft constraints below are used to calculate the fitness of the solution
            employees = []
            jobs = []
            
            # aggregate them by employee
            count = 0
            for task in self.task_list:

                idx = search(employees, task['employee'])
                if idx < 0:
                    employees.append( task['employee'] )
                    jobs.append( [ {'start': task['start'],
                                    'end': task['end'] } ] )
                else:
                    jobs[idx].append( {'start': task['start'],
                                    'end': task['end'] } )

                count += 1

            # calculate the overtime cost
            overtime_cost = 0
            emp = 0
            while emp < (len(employees)):
                sum_overtime = 0

                list_tasks = jobs[emp]
                list_ws = schedule.getEmployeeWorkShift(employees[emp])
                start_date = self.pop.start_date.strftime("%Y-%m-%d %H:%M")
                end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")

                emp_schedule = schedule.getSchedule( list_tasks, list_ws, start_date, end_date)

                for day in emp_schedule:
                    for period in day['list']:
                        if (period['type'] == 'overtime'):
                            p1 = period['start']
                            p2 = period['end']
                            tdelta = datetime.strptime(p2, '%H:%M') - datetime.strptime(p1, '%H:%M')
                            sum_overtime += tdelta.seconds / 60 # in minutes

                
                hourly_wage = getEmployeeHourlyWage( self, employees[emp] )
                overtime_cost += hourly_wage * (sum_overtime / 60) # in hours

                emp += 1

            self.employeeCost = overtime_cost

            
        # if consider Equipment Cost to calc fitness
        if (config.useEquipmentCost == True):

            equipments = []
            jobs = []

            # aggregate them by equpiment
            count = 0
            for task in self.task_list:

                idx = search(equipments, task['equipment'])
                if idx < 0:
                    equipments.append( task['equipment'] )
                    jobs.append( [ {'start': task['start'],
                                    'end': task['end'] } ] )
                else:
                    jobs[idx].append( {'start': task['start'],
                                    'end': task['end'] } )

                count += 1

            # calculate the stopped equipment cost
            overtime_cost = 0
            eqp = 0
            while eqp < (len(equipments)):
                sum_overtime = 0

                list_tasks = jobs[eqp]
                list_ws = schedule.getEquipmentWorkShift(equipments[eqp])
                start_date = self.pop.start_date.strftime("%Y-%m-%d %H:%M")
                end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")

                eqp_schedule = schedule.getSchedule( list_tasks, list_ws, start_date, end_date)

                for day in eqp_schedule:
                    for period in day['list']:
                        if (period['type'] == 'busy'):
                            p1 = period['start']
                            p2 = period['end']
                            tdelta = datetime.strptime(p2, '%H:%M') - datetime.strptime(p1, '%H:%M')
                            sum_overtime += tdelta.seconds / 60 # in minutes

                
                hourly_wage = getEquipmentHourlyCost( self, equipments[eqp] )
                overtime_cost += hourly_wage * (sum_overtime / 60) # in hours

                eqp += 1

            self.equipmentCost = overtime_cost


        # calculate the final fitness value
        self.fitness = round( self.employeeCost + self.equipmentCost, 2)


    def mutate(self):
        '''Mutate a chromosome changing its genes'''
        # The mutation movement consists of moving the task forward or backward
        # a number of time blocks, controlled by a 'pace' parameter, that defines
        # the radius of the movement, example:
        # -------oooo----------------------------- task position (timeline)
        # <<<<<<<oooo>>>>>>>>>>>>>>>>>><<<<<<<<<<< pace 1 = EXPLORATION
        # <<<<<<<oooo>>>>>>>>>------------------<< pace 0.5
        # ---<<<<oooo>>>>------------------------- pace 0.2 = EXPLOITATION

        #direction = (-1 if direction == 0 else 1)
        noChange = self.pop.ga.no_change_generations

        # define if use pace to get a directed mutation
        if (config.usePace == False):
            pace = 1.0
        else:
            if config.paceMethod == 1: # exploration -> exploitation
                if (noChange <= 15):
                    pace = 1 - noChange/17
                else:
                    pace = 1.0 if (noChange > 30) else ((noChange+3)/17 -1 )

            elif config.paceMethod == 0: # exploitation -> exploration
                if (noChange <= 15):
                    pace = (noChange+2)/17
                else:
                    pace = 0.1 if (noChange > 30) else (2 - (noChange+3)/17 )
        
        interval_max = int( ( self.limits[1] * (self.limits[0]+1) / 2 ) * pace)

        # defines if should use the whole range or just a width
        if config.usePaceWidth == True:
            interval = int( self.limits[1] * (self.limits[0]+1) / 2 )
            interval = int( interval * 0.2)
            interval_min = interval_max - interval
            interval_min = 1 if interval_min < 0 else interval_min
        else:
            interval_min = 1

        for i in range(1,self.length,2): # to get only the 'hour gene'
            
            # define if mutate, and the direction of the movemnt
            direction = random.randint(-1,1) #-1 backward, 0 no change, 1 forward
            
            # add the mutation value
            plus = int(random.randint( interval_min, interval_max) ) * direction
            self.addTimeBlocks(i,plus)

        return




    def checkHardConstraints(self):
        '''Check hard constraints that can invalidate the solution'''
        
        
        # if consider Employee Wage to calc fitness
        if (config.useEmployeeWage == True):

            # Rule 01 - check if there is overlap of jobs for a single employee
            employees = []
            emp_jobs = []

            # aggregate them by employee
            count = 0
            for task in self.task_list:

                idx = search(employees, task['employee'])
                if idx < 0:
                    employees.append( task['employee'] )
                    emp_jobs.append( [ {'start': task['start'],
                                    'end': task['end'] } ] )
                else:
                    emp_jobs[idx].append( {'start': task['start'],
                                    'end': task['end'] } )

                count += 1

            # then check the periods for each employee, searching for overlap
            overlap = False
            emp = 0
            while emp < (len(employees)):
                emp_jobs[emp].sort(key=sortingRule)
                count = 0
                while count < (len(emp_jobs[emp])-1):
                    if emp_jobs[emp][count]['end'] > emp_jobs[emp][count+1]['start']:
                        overlap = True
                        break
                    count += 1
                if overlap:
                    break
                emp += 1

            if overlap:
                self.fitness = -1
                return


        # if consider Equipment Cost to calc fitness
        if (config.useEquipmentCost == True):

            # Rule 02 - check if there is overlap of jobs for a single equipment
            equipments = []
            eqp_jobs = []
            
            # aggregate them by equipment
            count = 0
            for task in self.task_list:

                idx = search(equipments, task['equipment'])
                if idx < 0:
                    equipments.append( task['equipment'] )
                    eqp_jobs.append( [ {'start': task['start'],
                                    'end': task['end'] } ] )
                else:
                    eqp_jobs[idx].append( {'start': task['start'],
                                    'end': task['end'] } )

                count += 1

            # then check the periods for each equipment, searching for overlap
            overlap = False
            eqp = 0
            while eqp < (len(equipments)):
                eqp_jobs[eqp].sort(key=sortingRule)
                count = 0
                while count < (len(eqp_jobs[eqp])-1):
                    if eqp_jobs[eqp][count]['end'] > eqp_jobs[eqp][count+1]['start']:
                        overlap = True
                        break
                    count += 1
                if overlap:
                    break
                eqp += 1

            if overlap:
                self.fitness = -1
                return


        # Rule 03 - check if any period overflow the limit (end date)
        if (config.useEmployeeWage == True):
            group = employees
            jobs = emp_jobs
        elif (config.useEquipmentCost == True):
            group = equipments
            jobs = eqp_jobs
        
        idx = 0
        while idx < (len(group)):
            jobs[idx].sort(key=sortingRule)

            end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")
            if ( jobs[idx][-1]['end'] > end_date ):
                self.fitness = -1
                return
            idx += 1

        return


    # amount never can be greater than the amount of time blocs
    # multiplied by the amount of days (self.limits[0] * self.limits[1])
    # self - the chromosome object
    # position - the locus (only the one that controls time)
    # amount - the value to add or decrease
    def addTimeBlocks(self, position, amount):

        # define constants (positions of array 'genes')
        pos_day = position-1
        pos_time = position

        if (amount != 0): # if sums zero, does nothing
            
            # get new day and time considering the limit of time blocks
            new_time = (self.genes[pos_time]+amount) % (self.limits[1]+1)
            sum_day = (self.genes[pos_time]+amount) // (self.limits[1]+1)
            
            self.genes[pos_time] = new_time
            self.genes[pos_day] += sum_day
            
            if self.genes[pos_day] > self.limits[0]: # if greather than limit
                self.genes[pos_day] -= (self.limits[0] + 1)

            elif self.genes[pos_day] < 0: # if lower than start
                self.genes[pos_day] = self.limits[0]

        return