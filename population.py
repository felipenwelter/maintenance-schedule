#import time
#import numpy as np
#import operator
import random
import config
from datetime import datetime, timedelta
from chromosome import Chromosome
from gantt import showGantt
import jsonManipulate as jm
import json
import copy

def sortingRule(e):
  return e['date']

def search(list,value):
    try:
        return list.index(value)
    except ValueError:
        return -1


#def sortPopulation(newList: list):
    #'''ordena primeiro os valores fitness = true, depois value, depois weight, por exemplo:
    #true/19/29 - true/19/28 - true/18/30 - true 18/25 - true/18/25 - false/26/50'''
    #sortedList = sorted(
    #    newList, key=operator.attrgetter('weight'), reverse=True)
    #sortedList = sorted(
    #    sortedList, key=operator.attrgetter('value'), reverse=True)
    #sortedList = sorted(
    #    sortedList, key=operator.attrgetter("fitness"), reverse=True)
    #return sortedList


class Population:
    '''Classe que representa a população de uma geração com um determinado número de indivíduos (cromossomos)'''

    def __init__(self,ga):

        self.ga = ga

        self.chromosomes = []  # keep each chromosome (individuals)
        self.chromosome_length = 0 # composed by [days,time block] * number of service orders
        self.chromosome_limits = [0,0] # defined by number of days and number of time blocks
        self.size = config.population_size  # define the number of chromosomes (individuals) for the population
        
        self.so_list = {}
        self.start_date = ''
        self.end_date = ''
        self.total_days = 0

        self.list_fitness = [] # [chromosome position, fitness value]

        self.config() # set some configurations for the population
        
        

        # a média de peso dos indivíduos da população (informativo)
        #self.weightAverage = 0
        # método de procriação (geração de nova população)
        #self.procreateMethod = config.procreateMethod
        
        

    def initialize(self):
        '''inicializa a população de cromossomos com valores aleatórios'''
        for i in range(self.size):
            cromossomo = Chromosome(self)
            cromossomo.initialize()
            self.chromosomes.append(cromossomo)


        # fill the list_fitness (must me removed from here)
        # --------------------------------------------------
        self.list_fitness = []
        idx = 0
        # first identify which chromosomes gave best fitness
        while idx < len(self.chromosomes):
            c = self.chromosomes[idx]
            if c.fitness >= 0:
                self.list_fitness.append( [ idx, c.fitness ] )
            idx += 1
        
        if ( len(self.list_fitness) > 0 ):
            # order list by fitness (from better to worst)
            self.list_fitness.sort(key=lambda x: x[1])
            


    def config(self):

        # deep copy of the service order list
        self.so_list = []
        for li in self.ga.entry['service_orders']:
            d2 = copy.deepcopy(li)
            self.so_list.append(d2)


        #-----------------------------------------
        # to calculate the number of days
        start_date = ''
        end_date = ''

        # order the list of service_orders by start date
        self.so_list.sort(key=sortingRule)

        # identifies the first and last dates at all
        start_date = self.so_list[0]['date'] + " " + "00:00"
        end_date = self.so_list[-1]['date'] + " " + "23:59"
        dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        dt_end = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        self.start_date = dt
        self.end_date = dt_end

        # calculate the total of days (period)
        tot_days = (dt_end.date() - dt.date()).days
        self.total_days = tot_days + 1

        #-------------------------------------------------
        # to calculate the number of time blocks in a day
        tot_blocks = int( (60 / config.block_size) * 24 )
        #-----------------------------------------

        # update the limits for the genes
        self.chromosome_limits = [tot_days,tot_blocks]
        # update the number of genes in each chromosome
        self.chromosome_length = len(self.so_list) * len(self.chromosome_limits)

        #employees = []
        #for so in data['service_orders']:
        #    if search(employees, so['employee']) < 0:
        #        employees.append(so['employee'])

        #genes_employees = len("{0:b}".format( len(employees) ))
        #genes_days = len("{0:b}".format( (dt_end - dt).days )) 
        #genes_time = len("{0:b}".format(144)) #10min blocks (60/10 = 6 * 24 = 144)
        #genes_length = genes_days + genes_time # + genes_employees 
        
        #self.length = genes_length * len(data['service_orders'])
        #self.genes = [0 for i in range(self.length)]


    def gantt(self):
        
        for c in self.chromosomes:

            #count = 0
            #list_so = []
            #list_dates = []
            #for so in self.ga.entry['service_orders']:
                #obj = c.genes[ (count*2) : (count*2)+2 ]

                #so_day = obj[0]
                #so_time = obj[1]

                #start = self.start_date + timedelta(days=so_day)
                #start += timedelta(minutes=(so_time * config.block_size))
                #end = start + timedelta(hours=so['duration'])

                #list_so.append(so['number'])
                #list_dates.append([ start.strftime("%Y-%m-%d %H:%M"),
                #                    end.strftime("%Y-%m-%d %H:%M") ])
                #count += 1


            # aggregate the scheduled time to show gantt
            data = {}
            data['workload'] = []
            for so in c.so_list:
                data['workload'].append({
                            'number': so['number'],
                            'start': so['start'],
                            'end': so['end'],
                            'employee': so['employee']
                        })


            work_shift = jm.loadJSON_WS() #load list of work shifts from JSON

            showGantt(data,work_shift)
        
    #def evaluate(self):
        #'''Avalia cada cromossomo individualmente e recalcula seus atributos. Também realiza 
        ##cálculos relativos a própria população, como por exemplo a média de peso.'''
        #self.weightAverage = 0

        #for c in self.chromosomes:

        #    c.checkHardConstraints()
        #    c.calcFitness()



    def print(self):
        #'''Imprime em tela cada cromossomo da população e suas características principais '''
        # ordena pelo maior valor

        if ( len(self.list_fitness) > 0 ):
            pct = ( len(self.list_fitness) / config.population_size ) * 100
            print("total of feasible solutions: ", len(self.list_fitness),"(", int(pct) ,"% ) ")
            print("best fitness = ", self.list_fitness[0][1])
        else:
            print("no feasible solutions")
            
        #sortedList = sortPopulation(self.cromossomos)
        #for c in sortedList:
        #    print(
        #        f"composition {c.composition} weight {c.weight} | value {c.value} | %limit Weight {c.usedWeightPercent} | fitness {c.fitness}")
        #print(f" population weight average is {self.weightAverage} kg")


    def crossover(self, ancestral: object):
        #'''Geração de uma nova população a partir de uma população ancestral. Permite três formas diferentes:
        #- random: a seleção dos progenitores é feita de forma aleatória
        #- all_elite: todos os elementos que atendem ao critério fitness são copiados para a próxima geração
        #- first_elite: apenas o elemento mais próximo ao critério fitness é copiado para a próxima geração
        #em seguida é realizado o processo de crossover e mutação dos novos cromossomos, em casos específicos.'''

        #    # replica para a nova população todos os cromossomos que atendem criterio de fitness
        #    selected = []
        #    newList = sortPopulation(ancestral.cromossomos)
        #    for i in range(self.size):
        #        if (newList[i].fitness == True):
        #            self.cromossomos.append(newList[i])
        #        else:
        #            break

            # completa a população fazendo crossover dos cromossomos selecionados
        #    missingCromossomos = len(ancestral.cromossomos) - len(self.cromossomos)
        #    for i in range(missingCromossomos):
        #        p1, p2 = self.selectParents(selected if len(
        #            selected) > 0 else ancestral.cromossomos)
        #        new_cromossomo = self.crossover(p1, p2)
        #        new_cromossomo.mutate()  # mutação do novo cromossomo
        #        self.cromossomos.append(new_cromossomo)

        # select parents (chromosome position in self.chromosomes)
        c1, c2 = self.selectParents(ancestral)
        test = 0

        #if (self.procreateMethod == "random"):
        #    for i in range(self.size):
        #        # não replica nenhum item da população ancestral para a nova população
        #        p1, p2 = self.selectParents(ancestral.cromossomos)
        #        new_cromossomo = self.crossover(p1, p2)
        #        new_cromossomo.mutate()
        #        self.cromossomos.append(new_cromossomo)

        #elif (self.procreateMethod == "all_elite"):
        #    # replica para a nova população todos os cromossomos que atendem criterio de fitness
        #    selected = []
        #    newList = sortPopulation(ancestral.cromossomos)
        #    for i in range(self.size):
        #        if (newList[i].fitness == True):
        #            self.cromossomos.append(newList[i])
        #        else:
        #            break

        #    # completa a população fazendo crossover dos cromossomos selecionados
        #    missingCromossomos = len(
        #        ancestral.cromossomos) - len(self.cromossomos)
        #    for i in range(missingCromossomos):
        #        p1, p2 = self.selectParents(selected if len(
        #            selected) > 0 else ancestral.cromossomos)
        #        new_cromossomo = self.crossover(p1, p2)
        #        new_cromossomo.mutate()  # mutação do novo cromossomo
        #        self.cromossomos.append(new_cromossomo)

        #elif (self.procreateMethod == "first_elite"):
        #    # replica para a nova população somente o melhor cromossomo que atende ao criterio de fitness
        #    selected = []
        #    newList = sortPopulation(ancestral.cromossomos)
        #    if (newList[0].fitness == True):
        #        selected.append(newList[0])
        #        self.cromossomos.append(newList[0])

        #    # completa a população fazendo crossover dos cromossomos selecionados
        #    missingCromossomos = len(
        #        ancestral.cromossomos) - len(self.cromossomos)
        #    for i in range(missingCromossomos):
        #        p1, p2 = self.selectParents(selected if len(
        #            selected) > 0 else ancestral.cromossomos)
        #        new_cromossomo = self.crossover(p1, p2)
        #        new_cromossomo.mutate()  # mutação do novo cromossomo
        #        self.cromossomos.append(new_cromossomo)

    def selectParents(self, ancestor_pop: object) -> tuple: 
    #    '''Seleciona os pais para realizar o cruzamento. Busca os pais a partir de uma lista
    #    restrita de cromossomos de uma população anterior enviada como parâmetro.'''
    #    limit = len(cromossomoList)
    #    r = random.randint(0, limit-1)
    #    p1 = cromossomoList[r]
    #    s = random.randint(0, limit-1)
    #    p2 = cromossomoList[s]
        
        # what if there is no feasible parents or only one?
        limit = len(ancestor_pop.list_fitness)-1

        p1 = random.randint(0, limit)
        c1 = ancestor_pop.list_fitness[p1][0] # get the position of the chromosome in self.chromosomes
        
        p2 = random.randint(0, limit)
        c2 = ancestor_pop.list_fitness[p2][0] # get the position of the chromosome in self.chromosomes

        return c1, c2

    #def crossover(self, p1: object, p2: object) -> object:
    #    '''Faz cruzamento (crossover) unindo a primeira metade de genes do primeiro progenitor
    #    com a segunda meteade de genes do segundo progenitor'''
    #    half = int(p1.compositionSize/2)
    #    new_composition = p1.composition[:half] + p2.composition[half:]
    #    c = Cromossomo()
    #    c.composition = new_composition
    #    c.evaluate_fitness()  # atualiza características do cromossomo
    #    return c
