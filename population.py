import random
import config
from datetime import datetime, timedelta
from chromosome import Chromosome
from gantt import showEmployeeGantt, showEquipmentGantt
import jsonManipulate as jm
import json
import copy

# implementar custo de maquina parada
# implementar data fixa e % de variacao
# crossover de mais pontos!
# first solution - algo que tenha custo bom

# jogar autoAdjust pra dentro da classe de cromossomos mesmo?

def sortingRule(e):
  return e['date']

def sortbyFitness(e):
  return e.fitness

def search(list,value):
    try:
        return list.index(value)
    except ValueError:
        return -1


class Population:
    '''Classe que representa a população de uma geração com um determinado número de indivíduos (cromossomos)'''

    def __init__(self,ga):

        self.ga = ga # class GA of the population (to access parameters)

        self.chromosomes = []  # keep each chromosome (individuals)
        self.chromosome_length = 0 # composed by [days,time block] * number of tasks
        self.chromosome_limits = [0,0] # defined by number of days and number of time blocks
        self.size = config.population_size  # define the number of chromosomes (individuals) for the population
        
        self.task_list = {} # list of tasks
        self.start_date = '' # first day of the period to be alocated
        self.end_date = '' # last day of the period
        self.total_days = 0 # number of days (difference between end and start days)

        self.list_fitness = [] # [chromosome position, fitness value]
        self.no_change_generations = 0 # number of generations with no improvements

        self.config() # set some configurations for the population
        
        

    def initialize(self):
        '''Initialize the individuals with random values'''
        for i in range(self.size):
            cromossomo = Chromosome(self)
            cromossomo.initialize()
            self.chromosomes.append(cromossomo)
        
        self.updateFitnessList()
        self.ga.generation_count += 1



    def updateFitnessList(self):
        '''Update list_fitness with the feasible solutions'''

        self.list_fitness = [] # clear any current information
        idx = 0

        # identify which chromosomes have feasible fitness
        while idx < len(self.chromosomes):
            c = self.chromosomes[idx]
            if c.fitness >= 0:
                self.list_fitness.append( [ idx, c.fitness ] )
            idx += 1
        
        # order list by fitness (from better to worst)
        if ( len(self.list_fitness) > 0 ):
            self.list_fitness.sort(key=lambda x: x[1])
            


    def config(self):

        # deep copy of the tasks list
        self.task_list = []
        for li in self.ga.entry['tasks']:
            d2 = copy.deepcopy(li)
            self.task_list.append(d2)

        # order the list of tasks by start date
        #self.task_list.sort(key=sortingRule)

        #-----------------------------------------
        # to calculate the number of days
        start_date = self.ga.entry['period']['start'] + " " + "00:00" # ''
        end_date = self.ga.entry['period']['end'] + " " + "23:59" # ''

        # identifies the first and last dates at all
        dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        dt_end = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        self.start_date = dt
        self.end_date = dt_end

        # calculate the total of days (period)
        tot_days = (dt_end.date() - dt.date()).days
        self.total_days = tot_days + 1 # include last day

        #-------------------------------------------------
        # to calculate the number of time blocks in a day
        tot_blocks = int( (60 / config.block_size) * 24 )
        #-------------------------------------------------

        # update the limits for the genes
        self.chromosome_limits = [tot_days,tot_blocks-1]
        # update the number of genes in each chromosome
        self.chromosome_length = len(self.task_list) * len(self.chromosome_limits)



    def gantt(self):
        
        # check if there is at least one feasible solution
        if (self.getBestFitness() < 0):
            print("no feasible solutions to generate gantt")
            return

        c = self.chromosomes[self.list_fitness[0][0]] # pega o melhor individuo

        if (config.useEmployeeWage == True):
            # aggregate the scheduled time to show gantt
            data_emp = {}
            data_emp['workload'] = []
            for so in c.task_list:
                data_emp['workload'].append({
                            'number': so['number'],
                            'start': so['start'],
                            'end': so['end'],
                            'employee': so['employee']
                        })

            #load list of work shifts from JSON
            ws_emp = jm.loadJSON_employee_ws()

            showEmployeeGantt(data_emp,ws_emp)

        
        if (config.useEquipmentCost == True):
            # aggregate the scheduled time to show gantt
            data_eqp = {}
            data_eqp['workload'] = []
            for so in c.task_list:
                data_eqp['workload'].append({
                            'number': so['number'],
                            'start': so['start'],
                            'end': so['end'],
                            'equipment': so['equipment']
                        })

            #load list of work shifts from JSON
            ws_eqp = jm.loadJSON_equipment_ws()

            showEquipmentGantt(data_eqp,ws_eqp)


    def print(self):
        '''Print population info, only the best solution or all of them'''

        if ( len(self.list_fitness) > 0 ):
            pct = self.getFeasiblePct()
            print("total of feasible solutions: ", len(self.list_fitness),"(", int(pct) ,"% ) and",self.ga.no_change_generations,"no change - round",self.ga.generation_count )
            print("best fitness = ", self.list_fitness[0][1])
            for i in self.list_fitness:
                print(i[1], " ", self.chromosomes[i[0]].genes)
        else:
            print("no feasible solutions")


        

    def getFeasiblePct(self):
        if ( len(self.list_fitness) > 0 ):
            pct = ( len(self.list_fitness) / config.population_size ) * 100
        else:
            pct = 0
        return pct


    def generate(self, ancestor_pop: object):
        '''Generate a new population using the ancestor population, using crossover and mutation procedures'''
        
        #if self.ga.no_change_generations > 35:
        #    mutation_rate = 75
        #else:
        #    mutation_rate = 25

        mutation_rate = config.mutationRate
        rate = int(self.size * (mutation_rate/100))
        mutate_count = 0

        # select the best individual to copy to the new generation
        if (ancestor_pop.getBestFitness() >= 0):
            pos = ancestor_pop.list_fitness[0][0]
            chrom = copy.deepcopy( ancestor_pop.chromosomes[pos] )
            self.chromosomes.append(chrom)
            #print(chrom.genes, chrom.fitness)

        # complete the population with new individuals using crossover
        while len(self.chromosomes) < self.size:
            
            if (ancestor_pop.getBestFitness() >= 0):
                chroms = self.crossover(ancestor_pop)

                for chrom in chroms:

                    # mutate the new individuals (only the corresponding %)
                    if mutate_count < rate: # the mutation rate refers to the amount of individuals that suffers mutation
                        chrom.mutate() 
                        mutate_count += 1
                    
                    chrom.update()
                    
                    if len(self.chromosomes) >= 99:
                        a = 0

                    if len(self.chromosomes) < self.size:
                        self.chromosomes.append(chrom)

            else: # if there is still no feasible solution, generate randomly
                chrom = Chromosome(self)
                chrom.initialize()
                self.chromosomes.append(chrom)
            
            # print(chrom.genes, chrom.fitness, "of ", c1, c2)

        self.updateFitnessList()
        self.ga.generation_count += 1



    def crossover(self, ancestor_pop: object):
        '''Crossover ancestral information to generate new individuals'''

        # select parents (chromosome position in self.chromosomes)
        c1, c2 = self.selectParents(ancestor_pop)

        p1 = ancestor_pop.chromosomes[c1]
        p2 = ancestor_pop.chromosomes[c2]
    
        limit = len(ancestor_pop.task_list) # quantity of tasks
        locus_by_SO = int(self.chromosome_length / limit) # quantity of genes for each task
        cuts = random.sample(range(1,limit-1),k=2) # cut position
        cuts.sort()

        elements = random.sample([p1,p2], k=2) # shuffle parents

        pOrd1 = random.sample([0]*2+[1]*2, k=3)
        pOrd2 = [0 if (i == 1) else 1 for i in pOrd1]

        # generate 1st new chromosome
        genes =  elements[ pOrd1[0] ].genes[:( cuts[0] *locus_by_SO)]
        genes += elements[ pOrd1[1] ].genes[( cuts[0] *locus_by_SO):( cuts[1] *locus_by_SO)]
        genes += elements[ pOrd1[2] ].genes[( cuts[1] *locus_by_SO):]

        chrom1 = Chromosome(self)
        chrom1.genes = genes.copy()

        # generate 2nd new chromosome
        genes =  elements[ pOrd2[0] ].genes[:( cuts[0] *locus_by_SO)]
        genes += elements[ pOrd2[1] ].genes[( cuts[0] *locus_by_SO):( cuts[1] *locus_by_SO)]
        genes += elements[ pOrd2[2] ].genes[( cuts[1] *locus_by_SO):]

        chrom2 = Chromosome(self)
        chrom2.genes = genes.copy()
    
        return (chrom1, chrom2)


    def selectParents(self, ancestor_pop: object) -> tuple:
        '''Select parents for crossover using the ancestor population'''

        # in this case uses a random selection method among feasible individuals
        if (config.selectParentsMethod == 'random'): 

            limit = len(ancestor_pop.list_fitness)

            if (limit >= 2):
                parents = random.sample(range(0,limit),k=2) # return unique elements
            else:
                parents = random.choices(range(0,limit),k=2) # can repeat an element


            # randomly gets the chromosome position
            p1 = parents[0] #random.randint(0, limit)
            p2 = parents[1] #random.randint(0, limit)

            # uses the position to find the chromosome in self.chromosomes
            c1 = ancestor_pop.list_fitness[p1][0]
            c2 = ancestor_pop.list_fitness[p2][0]

            #print("number of good solutions = ", limit+1, "selected = ", p1, p2, p3)
        
        # in this case uses the roulette wheel method to select feasible parents
        else: #(config.selectParentsMethod == 'roulette'): 
            
            list_weight = [0] * len(ancestor_pop.list_fitness)
            limit = ancestor_pop.list_fitness[-1][1] * 1.5

            for i in range(0, len(list_weight) ):
                list_weight[i] = limit - ancestor_pop.list_fitness[i][1]
            
            sum_fitness = sum(i for i in list_weight)
            
            sum1 = random.randint(0, int(sum_fitness) )
            sum2 = random.randint(0, int(sum_fitness) )
            p1, p2 = -1, -1
            value, idx = 0, 0
            while (idx < len( list_weight ) ):
                value += list_weight[idx]
                if (p1 == -1) and (value >= sum1):
                    p1 = idx
                if (p2 == -1) and (value >= sum2):
                    p2 = idx
                if (p1 >= 0 and p2 >= 0):
                    break
                idx += 1

            # uses the position to find the chromosome in self.chromosomes
            c1 = ancestor_pop.list_fitness[p1][0]
            c2 = ancestor_pop.list_fitness[p2][0]

        return c1, c2



    def autoAdjust(self):
        ''' Função para realizar o refinamento do melhor indivíduo
        incialmente forcando uma mutation com passo baixo pra cada OS (double locus) individualmente
        testando hard constraints (feasible) a cada OS alterada
        a tendencia é convergir mais rapido, pois o refinamento passa a ser direcionado
        e nao depender do crossover e mutation'''
        passs = 1

        if len(self.list_fitness) > 0:
            
            c = self.chromosomes[ self.list_fitness[0][0] ]
            fitness = c.fitness
            
            for i in range(1,c.length,2): # apenas campos hora

                c.addTimeBlocks(i,passs)
                c.update() # update task list and calc fitness
                
                if c.fitness >= fitness: # piorou ou nao mudou
                    c.addTimeBlocks(i,-passs) # restaura
                    c.addTimeBlocks(i,-passs) # anda no sentido contrário
                    c.update() # update task list and calc fitness

                    while (c.fitness != -1) and (c.fitness < fitness):
                        print( "adjusting - ")
                        fitness = c.fitness
                        c.addTimeBlocks(i,-passs)
                        c.update() # update task list and calc fitness                  

                    c.addTimeBlocks(i,passs)
                    c.update() # update task list and calc fitness
                    fitness = c.fitness

                elif c.fitness < fitness: # melhorou

                    while (c.fitness != -1) and (c.fitness < fitness):
                        print( "adjusting + ")
                        fitness = c.fitness
                        c.addTimeBlocks(i,passs)
                        c.update() # update task list and calc fitness
                    
                    c.addTimeBlocks(i,-passs)
                    c.update() # update task list and calc fitness
                    fitness = c.fitness
            
            c.update() # update task list and calc fitness
            self.updateFitnessList()
            
        return


    def getBestFitness(self):
        '''Return the best fitness of the population'''
        fitness = -1
        if (self.list_fitness):
            fitness = self.list_fitness[0][1]
        return fitness