import config
from population import Population
import plot
import json
import time as t


#---------------------------------------------------------------
# Class geneticAlgorithm: execute genetic algorithm (G.A.) to
#   solve maintenance tasks scheduling (tasks/service orders)
#---------------------------------------------------------------
class geneticAlgorithm:

    def __init__(self):
        '''Initialize class opening configuration file'''

        self.entry = {}
        self.file_tasks = config.task_dataset

        self.no_change_generations = 0
        self.generation_count = 0
        self.bestGen = 0
        self.bestFitness = -1

        self.plot = True
        self.print = True

        self.startTime = t.time()
        self.bestTime = t.time()
        self.endTime = t.time()

        # Read json file and set some attributes for the population
        with open(f'datasets/{self.file_tasks}.json') as json_file:
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
        chronology_feasible.append( population.getFeasiblePct() )
        best_fitness = population.getBestFitness()
        chronology_fitness.append( best_fitness )

        # print information
        population.print()
        #population.gantt()


        # run generations (previously set) or until cost = 0
        for i in range(config.generations-1):

            # generate a new population based on the ancestor population
            newPop = Population(self)
            newPop.generate( population )
            #newPop.autoAdjust()
            
            # identify if there is any improvement
            new_fitness = newPop.getBestFitness()
            best_fitness = best_pop.getBestFitness()

            if (new_fitness != -1 and best_fitness != -1):
                if new_fitness < best_fitness:
                    if (config.autoAdjust):
                        newPop.autoAdjust()
                    best_pop = newPop
                    best_fitness = newPop.getBestFitness() # after auto adjustment
                    noChange = 0
                    self.bestTime = t.time()
                    self.bestGen = self.generation_count
                    self.bestFitness = best_fitness
                    #best_pop.gantt() #pra ver o que muda cada vez que melhora o fitness
                else:
                    noChange += 1
            else:
                if (best_fitness == -1 and new_fitness >= 0):
                    if (config.autoAdjust):
                        newPop.autoAdjust()
                    best_pop = newPop
                    best_fitness = newPop.getBestFitness() # after auto adjustment
                    noChange = 0
                    self.bestTime = t.time()
                    self.bestGen = self.generation_count
                    self.bestFitness = best_fitness
                    #best_pop.gantt() #pra ver o que muda cada vez que melhora o fitness
                #else:
                #    noChange += 1
            
            self.no_change_generations = noChange
            newPop.print()

            # store the best fitness of the population
            chronology_feasible.append( newPop.getFeasiblePct() )
            chronology_fitness.append( best_fitness )

            # identify if the solution converged to global miminum
            if (best_fitness == 0):
                print("converged - round", self.generation_count)
                break
            elif (noChange > config.exitAfter):
                print("exit after", config.exitAfter, "generations without improvements - round", self.generation_count)
                break
            
            # set the population for the next generation
            population = newPop
            
        self.endTime = t.time()
        
        if (self.plot == True):
            # show the last solution generated
            best_pop.gantt()

            # plot the evolution graph
            plot.plot(chronology_fitness,'cost')
            plot.plot(chronology_feasible,'feasible')
            #plot.plot(chronology_fitness,'cost',chronology_feasible)