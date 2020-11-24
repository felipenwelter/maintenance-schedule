#---------------------------------------------------------------
# Class geneticAlgorithm: execute genetic algorithm (G.A.) to
#   solve maintenance tasks scheduling (service orders)
#---------------------------------------------------------------

import config
from population import Population
import plot
import json


def getFeasibleQt(pop):
    if ( len(pop.list_fitness) > 0 ):
        pct = ( len(pop.list_fitness) / config.population_size ) * 100
    else:
        pct = 0
    return pct



class geneticAlgorithm:

    def __init__(self):
        '''Initialize class opening configuration file'''

        self.entry = {}
        self.file_so = config.service_order_dataset

        self.no_change_generations = 0

        # Read json file and set some attributes for the population
        with open(f'datasets/{self.file_so}.json') as json_file:
            self.entry = json.load(json_file)


    def run(self):
        '''Run G.A.'''

        # armazena o histórico de gerações
        chronology_fitness = [] # store the best fitness of each generation
        chronology_feasible = [] # store the number of feasible individuals of each generation
        noChange = 0 # control the number of rounds with no improvements

        # initialize a random population
        population = Population(self)
        population.initialize()
        chronology_fitness.append( population.list_fitness[0][1] )

        best_pop = population
        fitness = population.list_fitness[0][1]
        #population.gantt()

        #print(f"Initial Population")
        population.print()
        chronology_feasible.append( getFeasibleQt(population) )

        # run generations (previously set) or until cost = 0
        for i in range(config.generations-1):

            # generate a new population based on the ancestor
            newPop = Population(self)
            newPop.crossover( population )
            #newPop.autoAdjust()

            population = newPop

            if population.list_fitness[0][1] < best_pop.list_fitness[0][1]:
                population.autoAdjust()
                best_pop = population
                fitness = best_pop.list_fitness[0][1]
                noChange = 0
                #best_pop.gantt() #pra ver o que muda cada vez que melhora o fitness
            else:
                noChange += 1
            
            if fitness == 0:
                print("converged - round", i+1)
                break

            self.no_change_generations = noChange
            population.print()

            chronology_fitness.append( best_pop.list_fitness[0][1] )
            chronology_feasible.append( getFeasibleQt(population) )

        best_pop.gantt()

        plot.plot(chronology_fitness, chronology_feasible)
        