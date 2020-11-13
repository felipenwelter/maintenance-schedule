service_order_dataset = "entry"

#número de cromossomos (indivíduos) que deve existir em cada população gerada
population_size = 20

#número de gerações (rodadas)
generations = 500

#define o método para mutação de genes: "random", "fix" ou "none"
#mutateMethod = "random" 

#define o método de procriação (geração de nova população): "first_elite", "all_elite" ou "random"
#procreateMethod = "all_elite"

#for controlling the time scheduling, in minutes
block_size = 10 # in minutes (less than or equal 1 hour)