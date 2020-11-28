import random
import config
from datetime import datetime, timedelta
from chromosome import Chromosome
from gantt import showGantt
import jsonManipulate as jm
import json
import copy

# comentar e organizar funcoes
# setar metodo para mutate e crossover
# criar metodo externo para controlar pass size (e até mutation rate)
# implementar data fixa e % de variacao
# implementar custo de maquina parada
# montar readme

### TODO - crossover (order=weight) com mais pais, se tiver mais OS's, será que melhora?


#### TODO - trabalhar com a primeira solucao, ja forcar algo que tenha um custo bom

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

        # aggregate the scheduled time to show gantt
        data = {}
        data['workload'] = []
        for so in c.task_list:
            data['workload'].append({
                        'number': so['number'],
                        'start': so['start'],
                        'end': so['end'],
                        'employee': so['employee']
                    })


        work_shift = jm.loadJSON_WS() #load list of work shifts from JSON

        showGantt(data,work_shift)
        


    def print(self):
        '''Print population info, only the best solution or all of them'''

        if ( len(self.list_fitness) > 0 ):
            pct = self.getFeasiblePct()
            print("total of feasible solutions: ", len(self.list_fitness),"(", int(pct) ,"% ) and",self.ga.no_change_generations,"no change - round",self.ga.generation_count )
            print("best fitness = ", self.list_fitness[0][1])
            #for i in self.list_fitness:
            #    print(i[1], " ", self.chromosomes[i[0]].genes)
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
        for i in range(self.size - len(self.chromosomes) ):
            
            if (ancestor_pop.getBestFitness() >= 0):
                chrom = self.crossover(ancestor_pop)

                # mutate the new individuals (only the corresponding %)
                if mutate_count < rate: # the mutation rate refers to the amount of individuals that suffers mutation
                    chrom.mutate() 
                    mutate_count += 1
                
                chrom.update() 

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
        c1, c2, c3 = self.selectParents(ancestor_pop)

        p1 = ancestor_pop.chromosomes[c1]
        p2 = ancestor_pop.chromosomes[c2]
        p3 = ancestor_pop.chromosomes[c3]

        limit = len(ancestor_pop.task_list) # quantity of tasks
        locus_by_SO = int(self.chromosome_length / limit) # quantity of genes for each task
        cuts = random.sample(range(1,limit-1),k=2) # cut position
        cuts.sort()

        if (config.orderParentsMethod == 'random'):
            elements = random.sample([p1,p2,p3], k=3) # shuffle parents

        else: #if (config.orderParentsMethod == 'weight'):
            # organize the parents to use more genes of the parents with best fitness
            weight = [cuts[0], cuts[1]-cuts[0], limit-cuts[1]] # calculate number of genes between cuts
            parents = [p1,p2,p3]
            parents.sort(key=sortbyFitness) # sort parents: first the best fitness
            elements = [0,0,0] # final elements

            for a in range(0,3): # order the parents considering their fitness x genes used
                best = 0
                for b in range(1,3):
                    if (weight[b] > weight[best]):
                        best = b # identify the position with greater number of genes
                elements[best] = parents[a] # and define it to the parent with best fitness
                weight[best] = -1
        
        
        genes = elements[0].genes[:( cuts[0] *locus_by_SO)]
        genes += elements[1].genes[( cuts[0] *locus_by_SO):( cuts[1] *locus_by_SO)]
        genes += elements[2].genes[( cuts[1] *locus_by_SO):]

        chrom = Chromosome(self)
        chrom.genes = genes.copy()

        return chrom


    def selectParents(self, ancestor_pop: object) -> tuple:
        '''Select parents for crossover using the ancestor population'''

        # in this case uses a random selection method among feasible individuals
        if (config.selectParentsMethod == 'random'): 

            limit = len(ancestor_pop.list_fitness)

            if (limit >= 3): #TODO - NEM SEMPRE SE MOSTRA EFETIVO USAR PAIS DIFERENTES
                parents = random.sample(range(0,limit),k=3) # return unique elements
            else:
                parents = random.choices(range(0,limit),k=3) # can repeat an element


            # randomly gets the chromosome position
            p1 = parents[0] #random.randint(0, limit)
            p2 = parents[1] #random.randint(0, limit)
            p3 = parents[2] #random.randint(0, limit)

            # uses the position to find the chromosome in self.chromosomes
            c1 = ancestor_pop.list_fitness[p1][0]
            c2 = ancestor_pop.list_fitness[p2][0]
            c3 = ancestor_pop.list_fitness[p3][0]

            #print("number of good solutions = ", limit+1, "selected = ", p1, p2, p3)
        
        # in this case uses the roulette wheel method to select feasible parents
        else: #(config.selectParentsMethod == 'roulette'): 

            sum_fitness = sum(i[1] for i in ancestor_pop.list_fitness)
            sum1 = random.randint(0, int(sum_fitness) )
            sum2 = random.randint(0, int(sum_fitness) )
            sum3 = random.randint(0, int(sum_fitness) )
            p1, p2, p3 = -1, -1, -1
            value, idx = 0, 0
            while (idx < len( ancestor_pop.list_fitness) ):
                value += ancestor_pop.list_fitness[idx][1]
                if (p1 == -1) and (value >= sum1):
                    p1 = idx
                if (p2 == -1) and (value >= sum2):
                    p2 = idx
                if (p3 == -1) and (value >= sum3):
                    p3 = idx
                if (p1 >= 0 and p2 >= 0 and p3 >= 0):
                    break
                idx += 1

            # uses the position to find the chromosome in self.chromosomes
            c1 = ancestor_pop.list_fitness[p1][0]
            c2 = ancestor_pop.list_fitness[p2][0]
            c3 = ancestor_pop.list_fitness[p3][0]

        return c1, c2, c3



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