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
        
        

    def initialize(self):
        '''inicializa a população de cromossomos com valores aleatórios'''
        for i in range(self.size):
            cromossomo = Chromosome(self)
            cromossomo.initialize()
            self.chromosomes.append(cromossomo)
        
        self.updateFitnessList()



    def updateFitnessList(self):
        # fill the list_fitness

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



    def gantt(self):
        
        c = self.chromosomes[self.list_fitness[0][0]] # pega o melhor individuo

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

        # seleciona o melhor individuo para levar para a proxima populacao na íntegra
        pos = ancestral.list_fitness[0][0]
        cromossomo = copy.deepcopy( ancestral.chromosomes[pos] )
        self.chromosomes.append(cromossomo)
        #print(cromossomo.genes, cromossomo.fitness)

        # completa com individuos gerado por crossover
        rate = 0
        for i in range(self.size-1):

            # select parents (chromosome position in self.chromosomes)
            c1, c2 = self.selectParents(ancestral)

            p1 = ancestral.chromosomes[c1]
            p2 = ancestral.chromosomes[c2]

            limit = len(ancestral.so_list) #numero de OS
            locus_by_SO = int(self.chromosome_length / limit)
            cut = random.randint(0, limit-1)

            genes = p1.genes[:(cut*locus_by_SO)] + p2.genes[(cut*locus_by_SO):]

            cromossomo = Chromosome(self)
            cromossomo.genes = genes.copy()
            rate += cromossomo.mutate()

            cromossomo.updateSOList() #update service order list using the new genes
            cromossomo.calcFitness()

            self.chromosomes.append(cromossomo)

            #print(cromossomo.genes, cromossomo.fitness, "of ", c1, c2)
        
        self.updateFitnessList()
        rate = int( (rate / ((self.size-1) * (self.chromosome_length/2)) ) * 100)
        print("mutation rate = ", rate, "%")

        # TODO - depois criar uma rotina que força um auto-ajuste, quer dizer,
        # tenta ver as OS`s que estao pior e andar um pouquinho com elas pra ver se melhora



    def selectParents(self, ancestor_pop: object) -> tuple: 
    #    '''Seleciona os pais para realizar o cruzamento. Busca os pais a partir de uma lista
    #    restrita de cromossomos de uma população anterior enviada como parâmetro.'''


        if False:  # realiza uma selecao de pais aleatoria, dentre todos os individuos feasible

            # what if there is no feasible parents or only one?
            limit = len(ancestor_pop.list_fitness)-1

            p1 = random.randint(0, limit)
            c1 = ancestor_pop.list_fitness[p1][0] # get the position of the chromosome in self.chromosomes
            
            p2 = random.randint(0, limit)
            c2 = ancestor_pop.list_fitness[p2][0] # get the position of the chromosome in self.chromosomes

            #print("number of good solutions = ", limit+1, "selected = ", p1, p2)
        
        elif True: # metodo da roleta, entre os individuos feasible

            sum_fitness = sum(i[1] for i in ancestor_pop.list_fitness)
            sum1 = random.randint(0, int(sum_fitness) )
            sum2 = random.randint(0, int(sum_fitness) )
            p1, p2 = -1, -1, 
            soma, idx = 0, 0
            while (idx <= len( ancestor_pop.list_fitness) ):
                soma += ancestor_pop.list_fitness[idx][1]
                if (p1 == -1) and (soma >= sum1):
                    p1 = idx
                if (p2 == -1) and (soma >= sum2):
                    p2 = idx
                if (p1 >= 0 and p2 >= 0):
                    break
                idx += 1
                
            c1 = ancestor_pop.list_fitness[p1][0] # get the position of the chromosome in self.chromosomes
            c2 = ancestor_pop.list_fitness[p2][0] # get the position of the chromosome in self.chromosomes

            # what if there is no feasible parents or only one?


            # crossover randomico

            #if (len(ancestor_pop.list_fitness)-1 < 10):
            #    limit = len(ancestor_pop.list_fitness)-1
            #else:
            #    limit = 10

            #p1 = random.randint(0, limit)
            #c1 = ancestor_pop.list_fitness[p1][0] # get the position of the chromosome in self.chromosomes
            
            #p2 = random.randint(0, limit)
            #c2 = ancestor_pop.list_fitness[p2][0] # get the position of the chromosome in self.chromosomes

            #print("number of good solutions = ", limit+1, "selected = ", p1, p2)

        return c1, c2

