# Python code implementing the ICH (Information Content Heuristic) approximation algorithm for metric dimension (see [1])
# This code also applies to general multilateration problems (see [2])
# Code implementing a constructive algorithm for a bound on the metric dimension of Hamming graphs is included (see [2]) along with functions for testing resolvability
# [1] Hauptmann, M., Schmied, R., and Viehmann, C. Approximation complexity of metric dimension problem, Journal of Discrete Algorithms 14(2012), 214-222.
# [2] Tillquist, R. C., and Lladser, M. E. Low-dimensional representation of genomic sequences. Journal of Mathematical Biology (Mar 2019).

import numpy as np
import networkx as nx
from scipy.stats import entropy
from scipy.special import comb
from itertools import product, combinations, islice, repeat
import multiprocessing as mp
import pickle

########################
### READ/WRITE STATE ###
########################
# Save a snapshot of the algorithm state as a list of tuples (tags, chosen elements) using Python pickle
# input: tags - a dictionary of tags for each element based on the chosen columns
#       chosen - a list of the columns chosen so far
#       saveFile - name of the file to write to
#       overwrite - if true overwrite the contents of the file, otherwise append, default is False


def saveState(tags, chosen, saveFile, overwrite=False):
    L = [] if overwrite else readState(saveFile)
    L.append((tags, chosen))
    with open(saveFile, 'wb') as o:
        pickle.dump(L, o, protocol=pickle.HIGHEST_PROTOCOL)

# Read a list of saved states of the algorithm
# input: inFile - the file to read
# return: a list of (tag, chosen) pairs


def readState(inFile):
    L = []
    with open(inFile, 'rb') as f:
        L = pickle.load(f)
    return L

#####################
### ICH Algorithm ###
#####################
# Apply the ICH algorithm to approximate metric dimension or multilateration
# input: M - a list of lists, dictionary of dictionaries, or networkx graph object on which to perform the ICH algorithm
#           if a list of lists, the ICH algorithm will be applied directly
#           if a dictionary of dictionaries, the colNames argument will be used as a complete list of columns. if this is empty, an arbitrary key list from an elemt of M will be used
#           if a networkx graph object, the distance matrix will be used
#       colNames - optional list of columns. if M is a dictionary of dictionaries and colNames is not empty it will be used as the set of columns to consider, defaults to empty
#       dictDefault - optional default value to use if M is a dictionary of dictionaries, defaults to -1
#       useFullDistance - optional boolean value. if true and M is a graph, convert M to a list of lists before continuing. note that distances in the graph are assumed to be positive.
#                         if false, individual columns of a distance matrix are generated on demand in the colEntropy function
#       name - optional prefix to give to a file in which to save current state of the algorithm, defaults to empty
#       stateFile - optional name of a file to read current state from, default is empty
#       minFunc - optional string value indicating a method for selecting columns. Options are 'entropy' (default), 'equivalence class size', 'total variation distance', and 'number of collisions'
#       randOrder - optional boolean value. if true randomize the order in which columns are checked, defaults to true
#       procs - optional number of processes to run, defaults to 1
# return: a list of chosen columns representing a resolving set


def ich(M, colNames=[], dictDefault=-1, useFullDistance=True, name='', stateFile='', minFunc='entropy', randOrder=True, procs=1):
    progressFile = name+'_ich_progress'
    if name:
        saveState({}, [], progressFile, overwrite=True)
    if isinstance(M, nx.classes.graph.Graph) and useFullDistance:
        nodes = sorted(M.nodes())
        M = nx.floyd_warshall(M)
        M = [[int(M[u][v]) if (v in M and M[u][v] != np.inf)
              else -1 for v in nodes] for u in nodes]
    ### Start of ICH HERE! ###
    distr = {}
    tags = {}
    chosen = []
    #  stateFile - optional name of a file to read current state from
    # IGNORE
    if stateFile:
        (tags, chosen) = readState(stateFile)[-1]
        for t in tags:
            if tags[t] not in distr:
                distr[tags[t]] = []
            distr[tags[t]].append(t)
    elif isinstance(M, list) or isinstance(M, np.ndarray):
        tags = {i: '' for i in range(len(M))}
    elif isinstance(M, dict):
        tags = {i: '' for i in M}
    # HERE IS THE GRAPH OBJECT PART #
    elif isinstance(M, nx.classes.graph.Graph):
        # Dictionary that holds nodes as keys with empty items. (Items probably 
        # resolving group)
        tags = {i: '' for i in M.nodes()}
    # Total Number of Nodes
    n = len(tags)
    
    ### OLD ###
    # check = colNames if (isinstance(M, dict) and colNames) else (
    #     sorted(M[M.keys()[0]].keys()) if isinstance(M, dict) else sorted(tags.keys()))
    
    ### NEW ###
    # This variable will hold the final list of sorted keys
    check = None
    # Check if M is a dictionary and colNames has elements
    if isinstance(M, dict) and colNames:
        # If both conditions are true, use colNames directly
        check = colNames
    else:
        # If M is a dictionary but colNames is empty or missing
        if isinstance(M, dict):
            # Get the first key in M (assuming it's a non-empty dictionary)
            first_key = M.keys()[0]
            # Sort the keys of the value associated with the first key
            check = sorted(M[first_key].keys())
        else:
            # If M is not a dictionary, use sorted keys from a Dictionary named "tags"
            check = sorted(tags.keys())

        # Now "check" contains the sorted list of keys based on the conditions

    # Picks columns in the "chosen" list that have been considered for R?
    for col in chosen:
        check.remove(col)

    ### OLD ###
    # check = list(np.random.permutation(check)) if randOrder else sorted(check)
    
    # Update "check" with a random seq
    if randOrder:
        check = list(np.random.permutation(check))
    else: 
        sorted(check)
    # seq = [] #####
    while len(distr) < n and len(chosen) < n:
        # H to _
        (distr, tags, _, chosen) = pickColumn(M, tags, check,
                                              minFunc=minFunc, chosen=chosen, dictDefault=dictDefault, procs=procs)
        # print('check', check, chosen)
        check.remove(chosen[-1])
        # seq.append((chosen[-1], H))####
        if name:
            saveState(tags, chosen, progressFile, overwrite=True)
    if len(distr) < n and len(chosen) == n:
        return 'NO SOLUTION EXISTS'  # (chosen, seq)
    return chosen  # (chosen, seq)

# Determine the unchosen column optimizing the function described by minFunc (maximizing entropy by default)
# input: M - the object on which to perform multilateration
#       tags - tages given the columns already chosen
#       check - a list of columns left to check
#       minFunc - optional string value indicating a method for selecting columns. Options are 'entropy' (default), 'equivalence class size', 'total variation distance', and 'number of collisions'
#       chosen - optional list of already chosen columns, defaults to empty
#       dictDefault - optional default value to use if M is a dictionary of dictionaries, defaults to -1
#       procs - optional argument specifying the number of processes to use, defaults to 1
# return: the tag distribution with the new column, the new tags, the optimal value (wrt minFunc) with the new column, an updated list of chosen columns


def pickColumn(M, tags, check, minFunc="entropy", chosen=[], dictDefault=-1, procs=1):
    funcs = {'entropy': colEntropy, 'equivalence class size': equivSizes,
             'total variation distance': totalVariationDistance, 'number of collisions': numCollisions}
    func = funcs[minFunc]
    (valOpt, colOpt, distr) = (np.inf, -1, {}
                               ) if minFunc != 'entropy' else (-1, -1, {})
    if procs > 1:
        pool = mp.Pool(processes=procs)
        results = pool.map_async(
            func, [(col, M, tags, dictDefault) for col in check])
        results = results.get()
        pool.close()
        pool.join()
        (valOpt, colOpt, distr) = max(results)
    else:
        for col in check:
            (val, col, condDistr) = func((col, M, tags, dictDefault))
            # equivSizes((col, M, tags, dictDefault)) if minEquiv else colEntropy((col, M, tags, dictDefault))
            # print(val, valOpt, (minFunc=='entropy' and val > valOpt))
            if ((minFunc in ['equivalence class size', 'total variation distance', 'number of collisions']) and val < valOpt) \
                    or (minFunc == 'entropy' and val > valOpt):
                (valOpt, colOpt, distr) = (val, col, condDistr)  # more elegant?
    chosen.append(colOpt)
    if isinstance(M, list) or isinstance(M, np.ndarray):
        for t in tags:
            tags[t] += ';'+str(M[t][colOpt])
    elif isinstance(M, dict):
        for t in tags:
            tags[t] += ';'+str(M[t].get(colOpt, dictDefault))
    elif isinstance(M, nx.classes.graph.Graph):
        Dcol = nx.single_source_shortest_path_length(M, colOpt)
        for t in tags:
            tags[t] += ';'+str(Dcol.get(t, -1))
    return (distr, tags, valOpt, chosen)

# Determine the joint entropy resulting from adding a given column
# Input is given as a single tuple so map_async may be used from pickColumn
# input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
# return: the joint entropy, the column, and the distribution of tags


def colEntropy(args):
    (col, M, tags, dictDefault) = args
    def getSymbol(r, c): return ''
    Dcol = {}
    if isinstance(M, list) or isinstance(M, np.ndarray):
        def getSymbol(r, c): return M[r][c]
    elif isinstance(M, dict):
        def getSymbol(r, c): return M[r].get(c, dictDefault)
    elif isinstance(M, nx.classes.graph.Graph):
        Dcol = nx.single_source_shortest_path_length(M, col)
        def getSymbol(r, c): return Dcol.get(r, -1)
    jointDistr = {}
    for elem in tags:
        t = tags[elem]+';'+str(getSymbol(elem, col))
        if t not in jointDistr:
            jointDistr[t] = 0
        jointDistr[t] += 1
    e = entropy(list(jointDistr.values()), base=2)
    return (e, col, jointDistr)

# Determine the size of the largest equivalence class resulting from adding a given column
# Input is given as a single tuple so map_async may be used from pickColumn
# input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
# return: the size of the largest equivalence class, the column, and the distribution of tags


def equivSizes(args):
    (col, M, tags, dictDefault) = args
    def getSymbol(r, c): return ''
    Dcol = {}
    if isinstance(M, list) or isinstance(M, np.ndarray):
        def getSymbol(r, c): return M[r][c]
    elif isinstance(M, dict):
        def getSymbol(r, c): return M[r].get(c, dictDefault)
    elif isinstance(M, nx.classes.graph.Graph):
        Dcol = nx.single_source_shortest_path_length(M, col)
        def getSymbol(r, c): return Dcol.get(r, -1)
    jointDistr = {}
    e = 0
    for elem in tags:
        t = tags[elem]+';'+str(getSymbol(elem, col))
        if t not in jointDistr:
            jointDistr[t] = 0
        jointDistr[t] += 1
        if jointDistr[t] > e:
            e = jointDistr[t]
    return (e, col, jointDistr)

# Determine the total variation distance between a uniform and the distribution resulting from adding a given column
# Note, minimizing total variation distance and minimizing the size of the largest equivalence class should be the same
# (In particular, one of equivSizes and totalVariationDistance can call the other)
# Input is given as a single tuple so map_async may be used from pickColumn
# input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
# return: the total variation distance, the column, and the distribution of tags


def totalVariationDistance(args):
    (col, M, tags, dictDefault) = args
    def getSymbol(r, c): return ''
    Dcol = {}
    if isinstance(M, list) or isinstance(M, np.ndarray):
        def getSymbol(r, c): return M[r][c]
    elif isinstance(M, dict):
        def getSymbol(r, c): return M[r].get(c, dictDefault)
    elif isinstance(M, nx.classes.graph.Graph):
        Dcol = nx.single_source_shortest_path_length(M, col)
        def getSymbol(r, c): return Dcol.get(r, -1)
    jointDistr = {}
    delta = 0
    for elem in tags:
        t = tags[elem]+';'+str(getSymbol(elem, col))
        if t not in jointDistr:
            jointDistr[t] = 0
        jointDistr[t] += 1
        if jointDistr[t] > delta:
            delta = jointDistr[t]
    return (max(delta/len(M), 1./len(M)), col, jointDistr)

# Determine the number of collisions resulting from adding a given column
# Input is given as a single tuple so map_async may be used from pickColumn
# input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
# return: the number of collisions, the column, and the distribution of tags


def numCollisions(args):
    (col, M, tags, dictDefault) = args
    def getSymbol(r, c): return ''
    Dcol = {}
    if isinstance(M, list) or isinstance(M, np.ndarray):
        def getSymbol(r, c): return M[r][c]
    elif isinstance(M, dict):
        def getSymbol(r, c): return M[r].get(c, dictDefault)
    elif isinstance(M, nx.classes.graph.Graph):
        Dcol = nx.single_source_shortest_path_length(M, col)
        def getSymbol(r, c): return Dcol.get(r, -1)
    jointDistr = {}
    e = 0
    for elem in tags:
        t = tags[elem]+';'+str(getSymbol(elem, col))
        if t not in jointDistr:
            jointDistr[t] = 0
        jointDistr[t] += 1
        # if jointDistr[t] > e: e = jointDistr[t]
    e = sum(v*v for v in jointDistr.values())  # really v choose 2
    return (e, col, jointDistr)
