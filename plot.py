import matplotlib.pyplot as plt

#---------------------------------------------------------------
# Function plot:
#    Plot cost x generation graphic
# Parameters:
#    itens - cost of each generation
#    itens2 - number of feasible solutions at each generation
#---------------------------------------------------------------
def plot(itens=[], type='cost', itens2=[]):

    if type == 'cost':
        plt.plot(itens,'b')
        plt.ylabel('cost')
        plt.xlabel('generations')
        
    if type == 'feasible': 
        plt.plot(itens,'r')
        plt.ylabel('feasible %')
        plt.xlabel('generations')

    if itens2:
        plt.plot(itens2,'r')
    
    plt.show()