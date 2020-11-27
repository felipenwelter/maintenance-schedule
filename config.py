service_order_dataset = "entry"

# number of individuals for each population
population_size = 20

# number of generations (rounds)
generations = 50000

# for controlling the time scheduling, in minutes
block_size = 10 # in minutes (less than or equal 1 hour)

# define the parents selection method for crossover 
selectParentsMethod = 'random' # random or roulette
orderParentsMethod = 'random' # random or weight

# define mutation
mutationRate = 20