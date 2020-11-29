#---------------------------------------------------------------
# Main function to run the Genetic Algorithm class
#---------------------------------------------------------------

from ga import geneticAlgorithm

print("Agenda de Manutenção usando Algoritmo Genético")
print("Felipe Nathan Welter")
print("UDESC 2020 - Computação Natural")

results = []

#for i in range(1,10):
ga = geneticAlgorithm()
#ga.plot = False
ga.run()

#    r = ga.generation_count
#    results.append(r)

#print(results)
#print( round( sum(i for i in results) / len(results), 2) )