task_dataset = "entry"

# number of individuals for each population
population_size = 100

# number of generations (rounds)
generations = 1000

# for controlling the time scheduling, in minutes
block_size = 10 # in minutes (less than or equal 1 hour)

# define the parents selection method for crossover 
selectParentsMethod = 'roulette' # random or roulette
#orderParentsMethod = 'random' # random or weight

# define mutation (2~5)
mutationRate = 5