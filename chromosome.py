import random
import config
import json
from datetime import datetime, timedelta
import schedule
import copy

def search(list,value):
    try:
        return list.index(value)
    except ValueError:
        return -1

def sortingRule(e):
  return e['start']

class Chromosome:
    '''Classe que representa um indíviduo (cromossomo), sua composição de genes e suas características'''

    def __init__(self,pop):

        self.pop = pop
        #self.weight = 0  # peso do cromossomo (pela soma dos genes)
        #self.value = 0  # valor do cromossomo (pela soma dos genes)
        self.length = pop.chromosome_length # the chromosome lenght is calculated once in the population
        self.genes = [0 for i in range(self.length)] # initialize all genes as 0
        self.limits = pop.chromosome_limits  # defined by number ofdays and number of time blocks
        # atributo que define se cromosso atende critério de aceitação (fitness)
        self.fitness = 0

        # deep copy of the service order list
        self.so_list = []
        for li in self.pop.so_list:
            d2 = copy.deepcopy(li)
            self.so_list.append(d2)

        # atributo informativo para saber o percentual de ocupação em relação ao limite de peso
        #self.usedWeightPercent = 0
        #self.mutateMethod = config.mutateMethod  # método de mutação de genes

        # dados dos itens a serem avaliados para a mochila
        #self.file = config.dataset
        # valor dos itens da mochila (respectivo ao peso)
        #self.available_itens_value = []
        # peso dos itens da mochila (respectivo ao valor)
        #self.available_itens_weight = []
        # capacidade máxima de peso para a mochila, em kg
        #self.knapsackCapacity = 0
        # realiza a leitura do arquivo de dataset
        #self.readJson()

    def initialize(self):
        '''Define 0s and 1s randomly to compose the chromosome'''
        for i in range(self.length):
            if divmod(i,2)[1] == 0:
                self.genes[i] = random.randint(0, self.limits[0])
            else:
                self.genes[i] = random.randint(0, self.limits[1])

        self.updateSOList() #update service order list using the new genes
        self.calcFitness()



    def updateSOList(self):
        # convert the genes into readable day-time info
        # and save it in arrays list_so and list_dates
        count = 0
        list_so = []
        list_dates = []
        for so in self.pop.ga.so_list_original['service_orders']:
            obj = self.genes[ (count*2) : (count*2)+2 ]

            so_day = obj[0]
            so_time = obj[1]

            start = self.pop.start_date + timedelta(days=so_day)
            start += timedelta(minutes=(so_time * config.block_size))
            end = start + timedelta(hours=so['duration'])

            list_so.append(so['number'])
            list_dates.append([ start.strftime("%Y-%m-%d %H:%M"),
                                end.strftime("%Y-%m-%d %H:%M") ])
            count += 1

        # then use the saved arrays to append the start/end infos
        for so in self.so_list:
            idx = search(list_so, so['number'])
            so['start'] = list_dates[idx][0]
            so['end'] = list_dates[idx][1]


    def calcFitness(self):
        self.checkHardConstraints()


        employees = []
        jobs = []
        
        # aggregate them by employee
        count = 0
        for so in self.so_list:

            idx = search(employees, so['employee'])
            if idx < 0:
                employees.append( so['employee'] )
                jobs.append( [ {'start': so['start'],
                                'end': so['end'] } ] )
            else:
                jobs[idx].append( {'start': so['start'],
                                   'end': so['end'] } )

            count += 1

        # then check the periods for each employee, searching for overlap
        emp = 0
        while emp < (len(employees)):
            list_so = jobs[emp]
            list_ws = schedule.getWorkShift(employees[emp])
            start_date = self.pop.start_date.strftime("%Y-%m-%d %H:%M")
            end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")

            emp_schedule = schedule.getSchedule( list_so, list_ws, start_date, end_date)

            # TODO - identify overtime cost
            # TODO - identify stopped equipment cost
            
            emp += 1


        

    #def evaluate_fitness(self):
    #    '''Calcula e atualiza  as características do cromossomo'''
    #    self.value = 0
    #    self.weight = 0
    #    for i in range(self.compositionSize):
    #        # cada gene ativo '1' indica que peso e valor desse gene são somados no cromossomo
    #        if (self.composition[i] == 1):
    #            self.value += self.available_itens_value[i]
    #            self.weight += self.available_itens_weight[i]

    #    # calcula o percentual do peso que o cromossomo está usando em relação ao limite (carater informativo)
    #    # e se ultrapassar a capacidade da mochila, zera seu valor
    #    self.usedWeightPercent = (self.weight * 100) / \
    #        (self.knapsackCapacity)
    #    if (self.usedWeightPercent > 100):
    #        self.usedWeightPercent = 0
    #    self.usedWeightPercent = int(self.usedWeightPercent)

    #    # avalia se o cromossomo atende as expectativas de fitness (se não ultrapassa capacidade da mochila)
    #    if (self.weight <= self.knapsackCapacity):
    #        self.fitness = True
    #    else:
    #        self.fitness = False

    #def mutate(self):
    #    '''Método que realiza a mutação de um cromossomo, que pode ser feito de duas formas:
    #    - fix: define um grupo fixo de genes que sofrem mutação
    #    - random: define aleatoriamente quais genes sofrem mutação
    #    - none: não realiza nenhuma mutação'''
    #    if (self.mutateMethod == "fix"):
    #        self.fix_mutate()
    #    elif (self.mutateMethod == "random"):
    #        self.rand_mutate()
    #    self.evaluate_fitness()  # atualiza características do cromossomo

    #def fix_mutate(self):
    #    '''Faz a mutação dos genes centrais do cromossomo, assumindo valores aleatórios'''
    #    l = self.compositionSize//2
    #    i = l - (l//2)
    #    f = i + l
    #    for m in range(i, f):
    #        self.locus_change(m)

    #def rand_mutate(self):
    #    '''Faz a mutação de um número aleatório de genes, com valores aleatórios'''
    #    r = random.randint(0, self.compositionSize)
    #    for i in range(0, r):
    #        m = random.randint(0, self.compositionSize-1)
    #        self.locus_change(m)

    #def locus_change(self, m):
    #    '''Faz a mutação de um gene em específico para um valor aleatório'''
    #    self.composition[m] = random.randint(0, 1)





    def checkHardConstraints(self):

        # 01 - check if there is overlap of jobs for a single employee
        employees = []
        jobs = []
        
        # aggregate them by employee
        count = 0
        for so in self.so_list:

            idx = search(employees, so['employee'])
            if idx < 0:
                employees.append( so['employee'] )
                jobs.append( [ {'start': so['start'],
                                'end': so['end'] } ] )
            else:
                jobs[idx].append( {'start': so['start'],
                                   'end': so['end'] } )

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

        # 02 - check if any period overflow the limit (end date)
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

        # order the list of service_orders by start date
        data['service_orders'].sort(key=sortingRule)

        # identifies the first and last date at all
        start_date = data['service_orders'][0]['start'] + " " + "00:00"
        end_date = data['service_orders'][-1]['start'] + " " + "23:59"

        dt = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').date()
        dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').date()

        #employees = []
        #for so in data['service_orders']:
        #    if search(employees, so['employee']) < 0:
        #        employees.append(so['employee'])

        

        #genes_employees = len("{0:b}".format( len(employees) ))
        genes_days = len("{0:b}".format( (dt_end - dt).days )) 
        genes_time = len("{0:b}".format(144)) #10min blocks (60/10 = 6 * 24 = 144)
        genes_length = genes_days + genes_time # + genes_employees 
        
        self.length = genes_length * len(data['service_orders'])
        self.genes = [0 for i in range(self.length)]
