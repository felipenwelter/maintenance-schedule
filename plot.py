import matplotlib.pyplot as plt

def plot(itens, itens2):

    plt.plot(itens)
    plt.plot(itens2)
    plt.ylabel('cost')
    plt.xlabel('generations')
    plt.show()