#---------------------------------------------------------------
# Main function to run the Genetic Algorithm class
#---------------------------------------------------------------

from ga import geneticAlgorithm

print("Agenda de Manutenção usando Algoritmo Genético")
print("Felipe Nathan Welter")
print("UDESC 2020 - Computação Natural")

ga = geneticAlgorithm()
ga.plot = False
ga.run()
a = ga.generation_count