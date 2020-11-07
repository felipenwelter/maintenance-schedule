#from bruteForce import bruteForce
from ga import geneticAlgorithm
#import time as t

print("Agenda de Manutenção usando Algoritmo Genético")
print("Felipe Nathan Welter")
print("UDESC 2020 - Computação Natural")

#start = t.time()
#resp1 = bruteForce()
#time1 = t.time() - start

#start = t.time()
#resp2 = geneticAlgorithm()
ga = geneticAlgorithm()
ga.run()
#time2 = t.time() - start

#print(
#    f" \nbrute force spent {time1} sec to find {resp1.weight} kg to {resp1.value} of value")
#print(
#    f" genetic algorithm spent {time2} sec to find {resp2.weight} kg to {resp2.value} of value")
