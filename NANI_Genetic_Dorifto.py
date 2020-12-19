import random
import unittest

from deap import base, creator, tools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# The best way to summarize DEAP is that it gives the tools to create macros for classes.
# These 'macros' enable users to create a list of hundreds or thousands of containers represeting
# individuals and eneact custom coded functions on them such as selection.

#We are simulating genetic drift, so random fitness is fine.
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Registering tools to use on entire populations is the bread and butter of DEAP
toolbox.register("attr_bool", random.randint, 0, 1)

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 2)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#Random selection and 2 point crosses are essential for this simulation.
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("select", tools.selRandom)



def get_next_gen(pop):
    ''' This function will output the offspring of the input generation.
        The amount of offspring given will be equal to the starting population,
        so there will be no population growth or loss. '''


    # Perform selection on the offspring, with the DEAP library the selection is done first, then the cross.
    offspring = toolbox.select(pop, len(pop))

    # Will map a new independent instance of the offspring list to the old one, because the operators in Toolbox
    # will modify the original values, and need the originaL ones for reference.
    offspring = list(map(toolbox.clone, offspring))

    CROSSPROBABILITY = 0.5

    # Here we will cross the population in pairs.
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CROSSPROBABILITY:
            toolbox.mate(child1, child2)

    # Pass through the offspring.
    return offspring

def get_allele_freq(pop):
    ''' The allele for this population is either 1 or 0, so summing the genes
        in the population and dividing it by the population size is a quick way
        to get the allele frequencies. '''

    pop_sum = sum([individual[0] for individual in pop])

    return (pop_sum / len(pop))

def filter_input(raw_input):
    #''' Input sanitizer, will make sure the input is a positive integer. '''
    if raw_input.isdigit():
        if int(raw_input) > 0:
            return int(raw_input)

    print ("Invalid input!")
    return False

def data_gen(current_gen = 0):
    ''' This function is called everytime the animated graph needs a new point.
        The function will ask for a population size, the larger the size the slower
        the script will run. I recommend population sizes below 5k, and my cpu starts
        chugging at 10k. The max gen doesn't really have an affect on performance,
        but I've found 2-3 times the population size is usually enough. '''


    pop_size = False
    max_gen = False

    while pop_size == False:
        pop_size = filter_input(input("What's the population size? "))
    while max_gen == False:
        max_gen = filter_input(input("How many generations? "))

    pop = toolbox.population(n=pop_size)

    while current_gen < max_gen:
        current_gen += 1

        pop[:] = get_next_gen(pop)

        yield current_gen, get_allele_freq(pop)


def init():
    ''' Initial settings for our plot.'''

    plt.xlabel("Generations")
    plt.ylabel("Allele Frequencies")
    plt.title("Genetic Drift")

    #Allele frequencies are between 0 and 1, while the starting x-axis size of 10 is arbitrary
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []


def run(data):
    ''' This function will be called every interval period set in FuncAnimation.
        The function will update the graph parameters in our plot, which includes
        extending out the x-axis to match our current generation.
        The data fed into the function is given through the data_gen function.
    '''
    current_gen , y = data
    xdata.append(current_gen)
    ydata.append(y)
    xmin, xmax = ax.get_xlim()

    if current_gen >= xmax:
        ax.set_xlim(xmin, xmax + 50)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,

#This is the best way I've found to animate the graph in the way I want. The graph can be saved in the new window.
#When the script is run, it will ask for 2 inputs; population size and generation limit.
ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval= 10, repeat=False, init_func=init)
plt.show()

class TestFunc(unittest.TestCase):
    def test_filter(self):
        # Test function to make sure the input sanitizer is working
        self.assertEqual(filter_input("invalid input"), False)
        self.assertEqual(filter_input("-40"), False)
        self.assertEqual(filter_input("0"), False)
        self.assertEqual(filter_input("5"), 5)

    def test_get_allele_freq(self):
        # Test function to make sure correct allele frequencies are calculated.
        test_pop = [
        [1,1], [1,0], [1,1], [0,1], [1,1],
        ]
        self.assertEqual(get_allele_freq(test_pop), 0.8)

# V Uncomment for unit test V
#unittest.main()
