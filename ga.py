#---------------------------------------------------------------
# Class geneticAlgorithm: execute genetic algorithm (G.A.) to
#   solve maintenance tasks scheduling (service orders)
#---------------------------------------------------------------

import config
from population import Population
import plot
import json

class geneticAlgorithm:

    def __init__(self):
        '''Initialize class opening configuration file'''

        self.entry = {}
        self.file_so = config.service_order_dataset

        # Read json file and set some attributes for the population
        with open(f'datasets/{self.file_so}.json') as json_file:
            self.entry = json.load(json_file)


    def run(self):
        '''Run G.A.'''

        # armazena o histórico de gerações
        chronology = []
        feasible = []
        noChange = 0 # controla quantas geracoes o fitness nao melhora

        # inicializa uma população aleatoriamente
        population = Population(self)
        population.initialize()
        chronology.append( population.list_fitness[0][1] )

        best_pop = population
        fitness = population.list_fitness[0][1]
        #population.gantt()

        #print(f"Initial Population")
        pct = population.print()
        feasible.append(pct)

        #chronology.append(population)
        nRound = 0
        # executa as rodadas de sucessias gerações
        for i in range(config.generations-1):
            nRound += 1

            # generate a new population based on the ancestor
            newPop = Population(self)
            newPop.crossover( population, noChange )
            #newPop.autoAdjust()
            pct = newPop.print()

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
                print("converged - round", nRound)
                break

            chronology.append( best_pop.list_fitness[0][1] )
            feasible.append( pct )

        best_pop.gantt()

        plot.plot(chronology, feasible)
        