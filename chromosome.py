import random
import config
import json
from datetime import datetime, timedelta
import schedule
import copy

# TODO - identify stopped equipment cost            
# TODO - quando identificar que ficou preso num otimo local, aumenta o multiplicador 0,1 ali
# TODO - meu crossover ta ruim, porque pega qualquer um e nao só os bons!
  # provei isso quando usei populacoes de 100 elementos e fiquei preso em otimos globais, com 20 individuos zerei o custo (500 generations)

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
# Function getHourlyWage:
#    Return the hourly wage of a employee
# Parameters:
#    cr - chromosome
#    e - name of employee
#---------------------------------------------------------------
def getHourlyWage(cr,e):
    hourly_wage = 999
    for emp in cr.pop.ga.entry['employees']:
        if (emp['name'] == e):
            hourly_wage = float(emp['hourly-wage'])
    return hourly_wage


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
            list_ws = schedule.getWorkShift(employees[emp])
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

            
            hourly_wage = getHourlyWage( self, employees[emp] )
            overtime_cost += hourly_wage * (sum_overtime / 60) # in hours

            emp += 1

        self.fitness = round(overtime_cost,2)



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
        #noChange = self.pop.ga.no_change_generations

        #if (noChange <= 100):
            #pace = (noChange * noChange) / 2500 - (0.04 * noChange) + 1
        #    pace = ((9/25000) * (noChange * noChange)) - ((9/250) * noChange) + 1
        #else:
        #    pace = 1.0
        
        pace = 1.0

        # to avoid being locked in a local optimum, this function
        # navigate from exploration to exploitation  (0-50 generations)
        # and then from exploitation to exploration (51-100 generations)
        #   ^
        #   |(pass)
        # 1 |\     /-----
        #   | \   /
        # 0 |--\-/----> (noChange)
        #   0  50 100
        
        interval = int( ( self.limits[1] * (self.limits[0]+1) / 2 ) * pace)

        for i in range(1,self.length,2): # to get only the 'hour gene'
            
            # define if mutate, and the direction of the movemnt
            direction = random.randint(-1,1) #-1 backward, 0 no change, 1 forward
            
            # add the mutation value
            plus = int(random.randint( 1, interval) ) * direction
            self.addTimeBlocks(i,plus)

        return




    def checkHardConstraints(self):
        '''Check hard constraints that can invalidate the solution'''
        # Rule 01 - check if there is overlap of jobs for a single employee
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

        # then check the periods for each employee, searching for overlap
        overlap = False
        emp = 0
        while emp < (len(employees)):
            jobs[emp].sort(key=sortingRule)
            count = 0
            while count < (len(jobs[emp])-1):
                if jobs[emp][count]['end'] > jobs[emp][count+1]['start']:
                    overlap = True
                    break
                count += 1
            if overlap:
                break
            emp += 1

        if overlap:
            self.fitness = -1
            return

        # Rule 02 - check if any period overflow the limit (end date)
        emp = 0
        while emp < (len(employees)):
            jobs[emp].sort(key=sortingRule)

            end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")
            if ( jobs[emp][-1]['end'] > end_date ):
                self.fitness = -1
                return
            emp += 1

        return



    def readJson(self):
        with open(f'datasets/{self.file}.json') as json_file:
            data = json.load(json_file)
    #    self.knapsackCapacity = data["capacity"]
    #    self.available_itens_value = data["values"]
    #    self.available_itens_weight = data["weights"]

        start_date = ''
        end_date = ''

        # order the list of tasks by start date
        data['tasks'].sort(key=sortingRule)

        # identifies the first and last date at all
        start_date = data['tasks'][0]['start'] + " " + "00:00"
        end_date = data['tasks'][-1]['start'] + " " + "23:59"

        dt = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').date()
        dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').date()

        #employees = []
        #for task in data['tasks']:
        #    if search(employees, task['employee']) < 0:
        #        employees.append(task['employee'])

        

        #genes_employees = len("{0:b}".format( len(employees) ))
        genes_days = len("{0:b}".format( (dt_end - dt).days )) 
        genes_time = len("{0:b}".format(144)) #10min blocks (60/10 = 6 * 24 = 144)
        genes_length = genes_days + genes_time # + genes_employees 
        
        self.length = genes_length * len(data['tasks'])
        self.genes = [0 for i in range(self.length)]



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