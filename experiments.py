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
from multilateration import checkResolving

##################
### READ/WRITE ###
##################
# import geohat
# import sys
# sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/shelf/')
# import geopigeon
# import analysis

def readList(inFile):
    L = []
    with open(inFile, 'rb') as f:
        L = pickle.load(f)
    return L


def writeFile(data, outFile):
    with open(outFile, 'wb') as o:
        pickle.dump(data, o, protocol=pickle.HIGHEST_PROTOCOL)

# Random Algorithm
def randomSet(G):
  nodes = sorted(G.nodes())
  G = nx.floyd_warshall(G)
  G = [[int(G[u][v]) if (v in G and G[u][v]!=np.inf) else -1 for v in nodes] for u in nodes]
  nodes = set(nodes)
  R = [np.random.choice(list(nodes))]
  nodes.remove(R[0])
  while not checkResolving(R, G) and len(nodes) > 0:
    v = np.random.choice(list(nodes))
    R.append(v)
    nodes.remove(v)
  return R

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


import random
# Start and Stop given Range
def generate_random_floats(start, stop, num_values):
  random_values = [random.uniform(start, stop) for _ in range(num_values)]
  return random_values

# Start and Stop given Range
def generate_random_integers(start, stop, num_values):
  random_integers = [random.randint(start, stop) for _ in range(num_values)]
  return random_integers


num_values = 200

random_float_list = generate_random_floats(0.02, np.sqrt(2)+0.1, num_values=num_values)
random_integer_list = generate_random_integers(3, 23, num_values=num_values)


# Thoughts:
# - rgg_data_10.list == 10 repeats of N and R :)

if __name__ == '__main__':

    ### IMPORTANT ###
    dataFile = 'comeback_2_1_repeat_3_to_23nodes_200graphs.list'
    
    ## NOTE: IF YOU RUN EXPERIMENTS ON THE SAME FILE NAME WHICH HAS ALREADY DATA,
    ## IT WILL ADD UP. 200 graphs wanted. File had already 200, now file has 400 graphs. :/
    #################

    data = readList(dataFile) if glob.glob(dataFile) else []

    # Node Sizes
    nList = random_integer_list

    # Radius Amounts
    rList = random_float_list
    # rList = []

    repeats = 1

    # BELLOW THE THRESHOLD OLD CODE
    # for r in rList:
    #     # (Node, Threshold)
    #     nList.append(threshold.get_n_below_radius(
    #         starting_n=1, radius=r, repeat=repeats)[repeats-1][0])

    print('''
    You know the greatest danger facing us is ourselves, and irrational fear 
    of the unknown. There is no such thing as the unknown. Only things 
    temporarily hidden, temporarily not understood.
    -- Captain Kirk
    ''')

    # print('\nnList:', nList)
    # print('\nrList:', rList)
    # 92 
    # nList_sliced = nList[11:]
    # rList_sliced = rList[11:]
    # 25
    # 34 START
    # 12 work
    nList_sliced = nList
    rList_sliced = rList
    print('\nnList Sliced:', nList_sliced)
    print('\nrList Sliced:', rList_sliced)
    print('\n\n')
    counter = 0 
    for n, r in zip(nList_sliced, rList_sliced):
        for seed in np.random.randint(1, 1000000, size=countComplete(data, [(n, r)], repeats)[(n, r)]):
            print("\nNodes: ", n, "\nRadius: ", r, "\nSeed: ", seed)
            G = nx.random_geometric_graph(n, r, seed=int(seed))
            start = time.perf_counter()
            resSet = geo.ich(G)
            end = time.perf_counter()
            execution_time = (end - start)
            # matrix = analysis.get_distance_matrix(G=G)
            #print(matrix)
            # resSet, execution_time = geohat.get_stats_geohat(matrix=matrix, option=[1, 2, 3])
            # resSet, execution_time = geohat.get_stats_geohat(n, matrix=matrix)
            # start = time.perf_counter()
            # resSet = randomSet(G=G)
            # end = time.perf_counter()
            # execution_time = (end - start)
            counter += 1
            print('Time:', execution_time)
            data.append(
                (n, r, seed, resSet, execution_time,  G.nodes(data='pos')))

        # Write to File after sharing N and R with some seed(s) based on repeats.
        writeFile(data, dataFile)

    print(counter)
    print('\nExperiments Complete!\n')

    ### OLD METHOD ###
    # for n in nList:
    #     if n == -1:
    #         continue
    #     for r in rList:
    #         if r == 0.02 or r == 0.03:
    #             continue
    #         for seed in np.random.randint(1, 1000000, size=countComplete(data, [(n, r)], repeats)[(n, r)]):
    #             print("\nNodes: ", n, "\nRadius: ", r, "\nSeed: ", seed)
    #             G = nx.random_geometric_graph(n, r, seed=int(seed))
    #             start = time.perf_counter()
    #             resSet = geo.ich(G)
    #             end = time.perf_counter()
    #             execution_time = (end - start)
    #             print('Time:', execution_time)
    #             data.append(
    #                 (n, r, seed, resSet, execution_time,  G.nodes(data='pos')))

    #         # Write to File after sharing N and R with some seed(s) based on repeats.
    #         writeFile(data, dataFile)

    # print('\nExperiments Complete!\n')


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
# rList considered based on Tillquist recommendations.

# Notes:
# Excluded for now:
# - 0.02 (over 7000 min for whole list)
# - 0.03 (over 2000 min for whole list)
