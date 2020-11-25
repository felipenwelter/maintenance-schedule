import config
from population import Population
import plot
import json


#---------------------------------------------------------------
# Function getFeasiblePct:
#    Calculate and return the percentage of feasible solutions
# Parameters:
#    pop - population
#---------------------------------------------------------------
def getFeasiblePct(pop):
    if ( len(pop.list_fitness) > 0 ):
        pct = ( len(pop.list_fitness) / config.population_size ) * 100
    else:
        pct = 0
    return pct


#---------------------------------------------------------------
# Class geneticAlgorithm: execute genetic algorithm (G.A.) to
#   solve maintenance tasks scheduling (service orders)
#---------------------------------------------------------------
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

        # store the generations historic
        chronology_fitness = [] # store the best fitness of each generation
        chronology_feasible = [] # store the number of feasible individuals of each generation
        noChange = 0 # control the number of rounds with no improvements

        # initialize a random population
        population = Population(self)
        population.initialize()
        
        # store the best fitness of the population
        best_pop = population
        chronology_feasible.append( getFeasiblePct(population) )
        fitness = population.getBestFitness()
        chronology_fitness.append( fitness )

        # print information
        population.print()
        #population.gantt()


        # run generations (previously set) or until cost = 0
        for i in range(config.generations-1):

            # generate a new population based on the ancestor population
            newPop = Population(self)
            newPop.generate( population )
            #newPop.autoAdjust()

            population = newPop
            
            # identify if there is any improvement
            oldfit = population.getBestFitness()
            fitness = best_pop.getBestFitness()

            if oldfit < fitness:
                population.autoAdjust()
                best_pop = population
                fitness = fitness
                noChange = 0
                #best_pop.gantt() #pra ver o que muda cada vez que melhora o fitness
            else:
                noChange += 1
            
            # identify if the solution converged to global miminum
            if fitness == 0:
                print("converged - round", i+1)
                break

            self.no_change_generations = noChange
            population.print()
            
            # store the best fitness of the population
            chronology_feasible.append( getFeasiblePct(population) )
            chronology_fitness.append( fitness )
            
            

        best_pop.gantt()

        plot.plot(chronology_fitness, chronology_feasible)
        