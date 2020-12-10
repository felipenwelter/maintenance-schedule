task_dataset = "entry-small-1"

# number of individuals for each population
population_size = 40

# number of generations (rounds)
generations = 1000
exitAfter = 250

# for controlling the time scheduling, in minutes
block_size = 10 # in minutes (less than or equal 1 hour)

# define the parents selection method for crossover 
selectParentsMethod = 'roulette' # random or roulette

# define mutation (2~5)
mutationRate = 5
usePace = False
usePaceWidth = True #no need to change
paceMethod = 1 # 0 = exploitation -> exploration OR 1 = exploration -> exploitation;

# define fitness calc, one must be True
useEmployeeWage = True
useEquipmentCost = True

# try adjusting populations when there is any improvement
autoAdjust = True