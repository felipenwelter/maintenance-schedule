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

def getHourlyWage(cr,e):
    hourly_wage = 999
    for emp in cr.pop.ga.entry['employees']:
        if (emp['name'] == e):
            hourly_wage = float(emp['hourly-wage'])
    return hourly_wage

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
        for so in self.pop.ga.entry['service_orders']:
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

        # continue checking the soft constraints only if
        # passed through hard constraints
        if (self.fitness < 0):
            return

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

        # calculate the overtime cost
        overtime_cost = 0
        emp = 0
        while emp < (len(employees)):
            sum_overtime = 0

            list_so = jobs[emp]
            list_ws = schedule.getWorkShift(employees[emp])
            start_date = self.pop.start_date.strftime("%Y-%m-%d %H:%M")
            end_date = self.pop.end_date.strftime("%Y-%m-%d %H:%M")

            emp_schedule = schedule.getSchedule( list_so, list_ws, start_date, end_date)

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

        self.fitness = overtime_cost




            # TODO - identify stopped equipment cost        


    def mutate(self, noChange):
    #    '''Método que realiza a mutação de um cromossomo, que pode ser feito de duas formas:
    #    - fix: define um grupo fixo de genes que sofrem mutação
    #    - random: define aleatoriamente quais genes sofrem mutação
    #    - none: não realiza nenhuma mutação'''

# TODO - quando identificar que ficou preso num otimo local, aumenta o multiplicador 0,1 ali
# TODO - meu crossover ta ruim, porque pega qualquer um e nao só os bons!
  # provei isso quando usei populacoes de 100 elementos e fiquei preso em otimos globais, com 20 individuos zerei o custo (500 generations)
        for i in range(self.length):
            
            if divmod(i,2)[1] == 1: # altera a hora
                #if (random.randint(0,1) == 1): # aleatoriamente
                direction = random.randint(-1,1) #-1 backward, 0 no change, 1 forward
                #direction = (-1 if direction == 0 else 1)
                #passs = random.randint(0,10) /10
                
                ### PASSO INTEIRO
                #passs = 10 # 1% de self.limits[1]
                #plus = int( (passs / 100) * self.limits[1] )

    # TODO - o mutation rate deveria ser em relacao a todo o periodo válido,
    # e nao somente ao periodo limite de 1 dia
    # ex: limits[0]+1 = 2  X limits[1] = 144  == 288, ai nao precisaria somar dias
    # so fazer o controle a cada 144


    # outra forma seria, ao inves de usar timeblock aleatorio, direcionar para um
    # dos intervalos validos (idle) do calendario da pessoa, o que certamente seria bem mais complicado
    # e talvez seja até ruim quando tiver mais OS`s do que tempo # ou ainda alterar so as OS`s que estao ruins

                ### PASSO RANDOMICO, LIMITE % DE 144 (um dia)
                #passs = 0.5 # 1% de self.limits[1]
                #interval = int( self.limits[1] * (self.limits[0]+1) / 2 )
                #plus = int(random.randint(1, interval) * passs) * direction

                ### PASSO ajustado conforme noChange (preso em ótimos locais)
                # exploration 0.1 --- 1.0 exploitation
                
                if noChange > 50:
                #    a = 0
                    noChange = 0 # se ficou muito tempo preso, busca fora

#### TODO - trabalhar com a primeira solucao, ja forcar algo que tenha um custo bom

                noChangeLimit = 50 ## 35 geracoes sem mudanca, foca no exploitation (busca fora)
                noChange = noChangeLimit if noChange > noChangeLimit else noChange
                passs = 1 - (noChange / noChangeLimit) # pass%(x100) de self.limits[1]
                passs = 0.1 if passs == 0 else passs
                interval = int( ( self.limits[1] * (self.limits[0]+1) / 2 ) * passs)

                if passs >= 0.5: #busca fora
                    #plus = int(random.randint( int(interval/2), interval) ) * direction
                    plus = int(random.randint( 1, interval) ) * direction
                else: #refinamento
                    plus = int(random.randint( 1, interval) ) * direction


                if (plus != 0):
                    if (direction > 0): #forward

                        if (self.genes[i] + plus) > self.limits[1]: #se passar do limite do dia
                            self.genes[i] += plus - self.limits[1] # recomeca de 0h

                            if (self.genes[i-1] + 1) > self.limits[0]: # e soma 1 dia
                                self.genes[i-1] += 1 - self.limits[0]
                            else:
                                self.genes[i-1] += 1

                        else: #senao, só soma o tempo
                            self.genes[i] += plus

                    elif (direction < 0): #backward
                        
                        if (self.genes[i] + plus) < 0: #se passar do limite do dia
                            self.genes[i] += plus + self.limits[1] # recomeca de 0h

                            if (self.genes[i-1] - 1) < 0: # e soma 1 dia
                                self.genes[i-1] += self.limits[0]
                            else:
                                self.genes[i-1] -= 1

                        else: #senao, só soma o tempo
                            self.genes[i] += plus
        return
    
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
