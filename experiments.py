# Python code to collect data related to the metric dimension of random
# geometric graphs

import numpy as np
import networkx as nx
import multilateration as geo
from itertools import product
import multiprocessing as mp
import pickle
import glob
import time
import threshold

##################
### READ/WRITE ###
##################


def readList(inFile):
    L = []
    with open(inFile, 'rb') as f:
        L = pickle.load(f)
    return L


def writeFile(data, outFile):
    with open(outFile, 'wb') as o:
        pickle.dump(data, o, protocol=pickle.HIGHEST_PROTOCOL)

#############
### UTILS ###
#############
# determines the number of additional repeats necessary for each n,r pair in pairs
# input: data - a list of tuples (n, r, seed, resSet)
#       pairs - a list of tuples (n, r) to consider
#       repeats - the target number of repeats for each (n,r) pair
# return a dictionary (n,r)->(repeats - number of occurences in data)


def countComplete(data, pairs, repeats):
    counts = {pair: repeats for pair in pairs}
    for (n, r, _, _, _, _) in data:
        if (n, r) in counts:
            counts[(n, r)] -= 1
    return counts


# Thoughts:
# - rgg_data_10.list == 10 repeats of N and R :)

if __name__ == '__main__':

    ### IMPORTANT ###
    dataFile = 'rgg_data_10.list'
    #################

    data = readList(dataFile) if glob.glob(dataFile) else []

    # Node Sizes
    nList = []

    # Radius Amounts
    rList = list(np.arange(0.02, 0.14, 0.01)) + \
        list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))

    repeats = 10
    for r in rList:
        # (Node, Threshold)
        nList.append(threshold.get_n_below_radius(
            starting_n=1, radius=r, repeat=repeats)[repeats-1][0])

    print('''
    You know the greatest danger facing us is ourselves, and irrational fear 
    of the unknown. There is no such thing as the unknown. Only things 
    temporarily hidden, temporarily not understood.
    -- Captain Kirk
    ''')
    for n in nList:
        for r in rList:
            for seed in np.random.randint(1, 1000000, size=countComplete(data, [(n, r)], repeats)[(n, r)]):
                print("\nNodes: ", n, "\nRadius: ", r, "\nSeed: ", seed)
                G = nx.random_geometric_graph(n, r, seed=int(seed))
                start = time.perf_counter()
                resSet = geo.ich(G)
                end = time.perf_counter()
                execution_time = (end - start)
                print('Time:', execution_time)
                data.append(
                    (n, r, seed, resSet, execution_time,  G.nodes(data='pos')))

            # Write to File after sharing N and R with some seed(s) based on repeats.
            writeFile(data, dataFile)

    print('\nExperiments Complete!\n')


# Ideas:
# Compare ICU with our own created algorithms
# Exploratory Data Analysis with MatplotLib.

# nList =  list(range(100, 1001, 100)) + [2000, 5000] # to start consider smaller values
# NOTE: Forgot 5000 for the time being!!!!

# rList = list(np.arange(0.02, 0.14, 0.01)) + list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))
# repeats = 2 or 10 <-- seeds for r? 10 is ok for now.


##### MY THOUGHTS #####
# Repeats = 3, 5, 6, 7, 9, 10 (Pick the n number based on repeats and radius
# below threshold.)
# Starting_n = 1

# nList considered REMEMBER BELOW THRESHOLD ONLY based on radius repeat
# item value found in threshold.py list based on get n below radius?
# thoughts on this?????

# rList considered based on Tillquist recommendations.
