import matplotlib.pyplot as plt

#---------------------------------------------------------------
# Function plot:
#    Plot cost x generation graphic
# Parameters:
#    itens - cost of each generation
#    itens2 - number of feasible solutions at each generation
#---------------------------------------------------------------
def plot(itens, itens2):

    plt.plot(itens)
    plt.plot(itens2)
    plt.ylabel('cost')
    plt.xlabel('generations')
    plt.show()