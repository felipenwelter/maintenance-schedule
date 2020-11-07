#import random
import config
#from cromossomo import Cromossomo
from population import Population
#import plot
import json




class geneticAlgorithm:

    def __init__(self):

        self.so_list_original = {}
        self.file_so = config.service_order_dataset

        # Read json file and set some attributes for the population
        with open(f'datasets/{self.file_so}.json') as json_file:
            self.so_list_original = json.load(json_file)


    def run(self):
        # armazena o histórico de gerações
        #chronology = []

        # inicializa uma população aleatoriamente
        population = Population(self)
        population.initialize()
        
        #population.gantt()
        ### population.evaluate()

        #print(f"Initial Population")
        #population.print()

        #chronology.append(population)

        # executa as rodadas de sucessias gerações
        #for i in range(config.generations-1):

            # gera uma nova população baseada no antecessor
            #newPop = Population()
            #newPop.procreate(chronology[-1])
            #newPop.evaluate()

            #print(f"Population {i+1}")
            #newPop.print()

            #chronology.append(newPop)

        # imprime o gráfico para até 50 populações
        #if len(chronology) <= 50:
            # plot.plot(chronology)

        #best = chronology[-1].cromossomos[0]

        #print("Knapsack Problem - Genetic Algorithm")
        #print("A melhor resposta encontrada foi:")
        #print(f"composition: {best.composition}")
        #print(f"value: {best.value}")
        #print(f"weight: {best.weight}")

        #return best
        return True
        