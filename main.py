#---------------------------------------------------------------
# Main function to run the Genetic Algorithm class
#---------------------------------------------------------------

from ga import geneticAlgorithm

print("Agenda de Manutenção usando Algoritmo Genético")
print("Felipe Nathan Welter")
print("UDESC 2020 - Computação Natural")

results = []
totalrun = 10

for i in range(1,totalrun+1):
    print("#### running ",i, "of ", totalrun, "####")
    ga = geneticAlgorithm()
    ga.plot = False
    ga.print = False
    ga.run()

    #r = ga.generation_count
    #results.append(r)

    print(f"spent {ga.endTime - ga.startTime} sec to finish ")
    print(f"spent {ga.bestTime - ga.startTime} sec to find that answer {ga.bestFitness} ")
    print(f"best answer generation {ga.bestGen} and total generations {ga.generation_count} ")

#print(results)
#print( round( sum(i for i in results) / len(results), 2) )
