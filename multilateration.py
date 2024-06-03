#Python code implementing the ICH (Information Content Heuristic) approximation algorithm for metric dimension (see [1])
#This code also applies to general multilateration problems (see [2])
#Code implementing a constructive algorithm for a bound on the metric dimension of Hamming graphs is included (see [2]) along with functions for testing resolvability
#[1] Hauptmann, M., Schmied, R., and Viehmann, C. Approximation complexity of metric dimension problem, Journal of Discrete Algorithms 14(2012), 214-222.
#[2] Tillquist, R. C., and Lladser, M. E. Low-dimensional representation of genomic sequences. Journal of Mathematical Biology (Mar 2019).

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
#Save a snapshot of the algorithm state as a list of tuples (tags, chosen elements) using Python pickle
#input: tags - a dictionary of tags for each element based on the chosen columns
#       chosen - a list of the columns chosen so far
#       saveFile - name of the file to write to
#       overwrite - if true overwrite the contents of the file, otherwise append, default is False
def saveState(tags, chosen, saveFile, overwrite=False):
  L = [] if overwrite else readState(saveFile)
  L.append((tags, chosen))
  with open(saveFile, 'wb') as o:
    pickle.dump(L, o, protocol=pickle.HIGHEST_PROTOCOL)

#Read a list of saved states of the algorithm 
#input: inFile - the file to read
#return: a list of (tag, chosen) pairs
def readState(inFile):
  L = []
  with open(inFile, 'rb') as f:
    L = pickle.load(f)
  return L

#####################
### ICH Algorithm ###
#####################
#Apply the ICH algorithm to approximate metric dimension or multilateration
#input: M - a list of lists, dictionary of dictionaries, or networkx graph object on which to perform the ICH algorithm
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
#return: a list of chosen columns representing a resolving set
def ich(M, colNames=[], dictDefault=-1, useFullDistance=True, name='', stateFile='', minFunc='entropy', randOrder=True, procs=1):
  progressFile = name+'_ich_progress'
  if name: saveState({}, [], progressFile, overwrite=True)
  if isinstance(M, nx.classes.graph.Graph) and useFullDistance:
    nodes = sorted(M.nodes())
    M = nx.floyd_warshall(M)
    M = [[int(M[u][v]) if (v in M and M[u][v]!=np.inf) else -1 for v in nodes] for u in nodes]
  distr = {}
  tags = {}
  chosen = []
  if stateFile:
    (tags, chosen) = readState(stateFile)[-1]
    for t in tags:
      if tags[t] not in distr: distr[tags[t]] = []
      distr[tags[t]].append(t)
  elif isinstance(M, list) or isinstance(M, np.ndarray): tags = {i:'' for i in range(len(M))}
  elif isinstance(M, dict): tags = {i:'' for i in M}
  elif isinstance(M, nx.classes.graph.Graph): tags = {i:'' for i in M.nodes()}
  n = len(tags)
  check = colNames if (isinstance(M, dict) and colNames) else (sorted(M[M.keys()[0]].keys()) if isinstance(M, dict) else sorted(tags.keys()))
  for col in chosen: check.remove(col)
  check = list(np.random.permutation(check)) if randOrder else sorted(check)
  #seq = [] #####
  while len(distr) < n and len(chosen) < n:
    ####H to _
    (distr, tags, _, chosen) = pickColumn(M, tags, check, minFunc=minFunc, chosen=chosen, dictDefault=dictDefault, procs=procs)
    #print('check', check, chosen)
    check.remove(chosen[-1])
    #seq.append((chosen[-1], H))####
    if name: saveState(tags, chosen, progressFile, overwrite=True)
  if len(distr) < n and len(chosen) == n: return 'NO SOLUTION EXISTS' #(chosen, seq)
  return chosen #(chosen, seq)

#Determine the unchosen column optimizing the function described by minFunc (maximizing entropy by default)
#input: M - the object on which to perform multilateration
#       tags - tages given the columns already chosen
#       check - a list of columns left to check
#       minFunc - optional string value indicating a method for selecting columns. Options are 'entropy' (default), 'equivalence class size', 'total variation distance', and 'number of collisions'
#       chosen - optional list of already chosen columns, defaults to empty
#       dictDefault - optional default value to use if M is a dictionary of dictionaries, defaults to -1
#       procs - optional argument specifying the number of processes to use, defaults to 1
#return: the tag distribution with the new column, the new tags, the optimal value (wrt minFunc) with the new column, an updated list of chosen columns
def pickColumn(M, tags, check, minFunc="entropy", chosen=[], dictDefault=-1, procs=1):
  funcs = {'entropy':colEntropy, 'equivalence class size':equivSizes, 'total variation distance':totalVariationDistance, 'number of collisions':numCollisions}
  func = funcs[minFunc]
  (valOpt, colOpt, distr) = (np.inf, -1, {}) if minFunc!='entropy' else (-1, -1, {})
  if procs > 1:
    pool = mp.Pool(processes=procs)
    results = pool.map_async(func, [(col, M, tags, dictDefault) for col in check])
    results = results.get()
    pool.close()
    pool.join()
    (valOpt, colOpt, distr) = max(results)
  else:
    for col in check:
      (val, col, condDistr) = func((col, M, tags, dictDefault))
      #equivSizes((col, M, tags, dictDefault)) if minEquiv else colEntropy((col, M, tags, dictDefault))
      #print(val, valOpt, (minFunc=='entropy' and val > valOpt))
      if ((minFunc in ['equivalence class size', 'total variation distance', 'number of collisions']) and val < valOpt) \
          or (minFunc=='entropy' and val > valOpt): (valOpt, colOpt, distr) = (val, col, condDistr) #more elegant?
  chosen.append(colOpt)
  if isinstance(M, list) or isinstance(M, np.ndarray):
    for t in tags: tags[t] += ';'+str(M[t][colOpt])
  elif isinstance(M, dict):
    for t in tags: tags[t] += ';'+str(M[t].get(colOpt, dictDefault))
  elif isinstance(M, nx.classes.graph.Graph):
    Dcol = nx.single_source_shortest_path_length(M, colOpt)
    for t in tags: tags[t] += ';'+str(Dcol.get(t, -1))
  return (distr, tags, valOpt, chosen)

#Determine the joint entropy resulting from adding a given column
#Input is given as a single tuple so map_async may be used from pickColumn
#input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
#return: the joint entropy, the column, and the distribution of tags
def colEntropy(args):
  (col, M, tags, dictDefault) = args
  getSymbol = lambda r,c: ''
  Dcol = {}
  if isinstance(M, list) or isinstance(M, np.ndarray): getSymbol = lambda r,c: M[r][c]
  elif isinstance(M, dict): getSymbol = lambda r,c: M[r].get(c, dictDefault)
  elif isinstance(M, nx.classes.graph.Graph):
    Dcol = nx.single_source_shortest_path_length(M, col)
    getSymbol = lambda r,c: Dcol.get(r, -1)
  jointDistr = {}
  for elem in tags:
    t = tags[elem]+';'+str(getSymbol(elem, col))
    if t not in jointDistr: jointDistr[t] = 0
    jointDistr[t] += 1
  e = entropy(list(jointDistr.values()), base=2)
  return (e, col, jointDistr)

#Determine the size of the largest equivalence class resulting from adding a given column
#Input is given as a single tuple so map_async may be used from pickColumn
#input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
#return: the size of the largest equivalence class, the column, and the distribution of tags
def equivSizes(args):
  (col, M, tags, dictDefault) = args
  getSymbol = lambda r,c: ''
  Dcol = {}
  if isinstance(M, list) or isinstance(M, np.ndarray): getSymbol = lambda r,c: M[r][c]
  elif isinstance(M, dict): getSymbol = lambda r,c: M[r].get(c, dictDefault)
  elif isinstance(M, nx.classes.graph.Graph):
    Dcol = nx.single_source_shortest_path_length(M, col)
    getSymbol = lambda r,c: Dcol.get(r, -1)
  jointDistr = {}
  e = 0
  for elem in tags:
    t = tags[elem]+';'+str(getSymbol(elem, col))
    if t not in jointDistr: jointDistr[t] = 0
    jointDistr[t] += 1
    if jointDistr[t] > e: e = jointDistr[t]
  return (e, col, jointDistr)

#Determine the total variation distance between a uniform and the distribution resulting from adding a given column
#Note, minimizing total variation distance and minimizing the size of the largest equivalence class should be the same
#(In particular, one of equivSizes and totalVariationDistance can call the other)
#Input is given as a single tuple so map_async may be used from pickColumn
#input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
#return: the total variation distance, the column, and the distribution of tags
def totalVariationDistance(args):
  (col, M, tags, dictDefault) = args
  getSymbol = lambda r,c: ''
  Dcol = {}
  if isinstance(M, list) or isinstance(M, np.ndarray): getSymbol = lambda r,c: M[r][c]
  elif isinstance(M, dict): getSymbol = lambda r,c: M[r].get(c, dictDefault)
  elif isinstance(M, nx.classes.graph.Graph):
    Dcol = nx.single_source_shortest_path_length(M, col)
    getSymbol = lambda r,c: Dcol.get(r, -1)
  jointDistr = {}
  delta = 0
  for elem in tags:
    t = tags[elem]+';'+str(getSymbol(elem, col))
    if t not in jointDistr: jointDistr[t] = 0
    jointDistr[t] += 1
    if jointDistr[t] > delta: delta = jointDistr[t]
  return (max(delta/len(M), 1./len(M)), col, jointDistr)

#Determine the number of collisions resulting from adding a given column
#Input is given as a single tuple so map_async may be used from pickColumn
#input: col - the column to add
#       M - the object on which to perform multilateration
#       tags - tags given the columns already chosen
#       dictDefault - default value to use if M is a dictionary of dictionaries
#return: the number of collisions, the column, and the distribution of tags
def numCollisions(args):
  (col, M, tags, dictDefault) = args
  getSymbol = lambda r,c: ''
  Dcol = {}
  if isinstance(M, list) or isinstance(M, np.ndarray): getSymbol = lambda r,c: M[r][c]
  elif isinstance(M, dict): getSymbol = lambda r,c: M[r].get(c, dictDefault)
  elif isinstance(M, nx.classes.graph.Graph):
    Dcol = nx.single_source_shortest_path_length(M, col)
    getSymbol = lambda r,c: Dcol.get(r, -1)
  jointDistr = {}
  e = 0
  for elem in tags:
    t = tags[elem]+';'+str(getSymbol(elem, col))
    if t not in jointDistr: jointDistr[t] = 0
    jointDistr[t] += 1
    #if jointDistr[t] > e: e = jointDistr[t]
  e = sum(v*v for v in jointDistr.values()) #really v choose 2
  return (e, col, jointDistr)

###################
### BRUTE FORCE ###
###################
#Find the metric dimension of a graph via brute force
#Consider all subsets of nodes of size startK
#The multiprocessing is accomplished by focusing on groups column combinations so that 
#the process can stop early if a resolving set is discovered. Taking advantage of other
#facilities in the multiprocessing library, like Queues, may be a more appropriate approach
#input: M - the object on which to perform multilateration
#       startK - optional argument specifying the size of column subsets to consider first, defaults to 1
#       chunkSize - optional argument specifying the number of subsets of columns to consider at a time
#                   before a check is done to verify that no resolving set has been discovered before
#                   continuing, defaults to 1000
#       procs - optional argument specifying the number of processes to use, defaults to 1
#return: a resolving set if one is found and 'NO SOLUTION EXISTS' otherwise
def bruteForce(M, startK=1, chunkSize=1000, procs=1):
  if isinstance(M, nx.classes.graph.Graph):
    nodes = sorted(M.nodes())
    M = nx.floyd_warshall(M)
    M = [[int(M[u][v]) if (v in M and M[u][v]!=np.inf) else -1 for v in nodes] for u in nodes]
  resSet = []
  while len(resSet)==0 and startK<=len(M):
    resSet = bruteForceK(M, startK, chunkSize=chunkSize, procs=procs)
    startK += 1
  return resSet if startK<=len(M) else 'NO SOLUTION EXISTS'

#A helper function for bruteForce that checks a chunk of column subsets for resolvability
#input: M - the object on which to perform multilateration
#       k - the size of column subsets to consider as potential resolving sets
#       chunkSize - optional argument specifying the number of subsets of columns to consider at a time
#                   before a check is done to verify that no resolving set has been discovered before
#                   continuing, defaults to 1000
#       procs - optional argument specifying the number of processes to use, defaults to 1
#return: a resolving set if one is discovered and an empty list otherwise
def bruteForceK(M, k, chunkSize=1000, procs=1):
  tot = float(comb(len(M), k))
  combos = combinations(range(len(M)), k)
  chunk = list(islice(combos, chunkSize))
  num = 0
  while len(chunk) > 0:
    if num % 10 == 0: print('  k: '+str(k)+', chunk '+str(num)+', fraction complete: '+str(num*chunkSize/tot))
    num += 1

    pool = mp.Pool(processes=procs)
    results = pool.map_async(checkRes, zip(chunk, repeat(M)))
    results = results.get()
    pool.close()
    pool.join()

    for (resolved, resSet) in results:
      if resolved: return list(resSet)
    chunk = list(islice(combos, chunkSize))
  return []

#A wrapper function to call checkResolving for a brute force search
#input: args - a tuple containing the set of columns to consider and the matrix
#return: (true if R is a resolving set of M and false otherwise, the tested columns)
def checkRes(args):
  (R, M) = args
  return (checkResolving(R, M), R)

######################
### HAMMING GRAPHS ###
######################
#Computes the hamming distance or number of mismatches between two strings
#If one string is longer the other, only its prefix is used
#input: a, b - two sequences to compare
#return: the hamming distance between a and b
def hammingDist(a, b):
  return sum(1 for (x,y) in zip(a,b) if x!=y)

#Given a resolving set of a Hamming graph H(k, a), determine a resolving set for H(k+1, a) (see [2])
#input: resSet - a resolving set for H(k, a)
#       alphabet - the alphabet from which to draw characters for the new resolving set
#       rand - optional boolean, if true randomize resSet and alphabet order, default is false
#return: a resolving set for H(k+1, a)
def hammingConstruction(resSet, alphabet, rand=False):
  alphabet = [[a] for a in alphabet]
  if len(resSet)==0: return alphabet[:-1]
  if rand:
    resSet = map(list, np.random.permutation(resSet))
    alphabet = map(list, np.random.permutation(alphabet))
  newResSet = [r+alphabet[2*i] if 2*i<len(alphabet) else r+alphabet[0] for i,r in enumerate(resSet)]
  num = len(alphabet) / 2
  for i in range(num):
    v = resSet[i]+alphabet[2*i+1]
    newResSet.append(v)
  return newResSet

#Find all resolving sets of a Hamming graph via a brute force search for a particular size
#This may be extremely slow even for small values of k and alphabet
#input: k - the length of strings in the hamming graph
#       alphabet - the alphabet to use in the hamming graph
#       size - the size of sets to check
#       procs - the number of processes to use, default is 1
#       verbose - optional bool. if true and procs=1, print percent of sets checked every 10000 sets, default is false
#return: all resolving sets of the given size for the specified hamming graph
def hammingAllResolving(k, alphabet, size, procs=1, verbose=False):
  if isinstance(alphabet, str): alphabet = list(alphabet)
  resSets = []
  kmers = product(alphabet, repeat=k)
  if procs>1:
    pool = mp.Pool(processes=procs)
    results = pool.map_async(checkResolvingHammingTuple, zip(combinations(kmers, size), repeat(k), repeat(alphabet)))
    results = results.get()
    pool.close()
    pool.join()
    for (isResolving, R) in results:
      if isResolving: resSets.append(R)
  else:
    numCombos = comb(int(np.power(len(alphabet), k)), size)
    for i,R in enumerate(combinations(kmers, size)):
      if verbose and i%10000==0: print('Brute force progress: ', i / numCombos)
      if checkResolvingHamming(R, k, alphabet, verbose=verbose): resSets.append(R)
  return resSets

#A helper function accepting a tuple of arguments for checkResolvingHamming
#This allows pool.map_async to be used for multiprocessing
#input: a tuple containing 3 elements
#       R - a set of strings to check as resolving
#       k - length of strings
#       alphabet - characters that strings are composed of
#return: immediately calls checkResolvingHamming and returns the result in addition to the given set R
def checkResolvingHammingTuple(args):
  (R, k, alphabet) = args
  return (checkResolvingHamming(R, k, alphabet), R)

#Check that a given set of strings is resolving for a specified Hamming graph
#This may be extremely slow even for small values of k and alphabet
#input: R - a set of strings to check as resolving
#       k - length of strings
#       alphabet - characters that strings are composed of
#       procs - optional number of processes to use, default is 1
#       chunkSize - optional number of strings to check at once if procs>1, default is 1000
#       verbose - optional bool. if true, print percent of strings checked every 10000 sets or every chunkSize if procs>1, default is false
def checkResolvingHamming(R, k, alphabet, procs=1, chunkSize=1000, verbose=False):
  if isinstance(alphabet, str): alphabet = list(alphabet)
  tags = {}
  if procs>1:
    kmers = zip(product(alphabet, repeat=k), repeat(R))
    chunk = list(islice(kmers, 0, chunkSize))
    chunkNum = 0
    while len(chunk)>0:
      if verbose:
        print('Check resolving Hamming progress: chunk', chunkNum)
        chunkNum += 1
      pool = mp.Pool(processes=procs)
      results = pool.map_async(genTag, chunk)
      results = results.get()
      pool.close()
      pool.join()
      for tag in results:
        if tag in tags: return False
        tags[tag] = 1
      chunk = list(islice(kmers, 0, chunkSize))
  else:
    tot = float(np.power(len(alphabet), k))
    for i,seq in enumerate(product(alphabet, repeat=k)):
      if verbose and i%10000==0: print('Check resolving Hamming progress: ', i/tot)
      tag = ';'.join(map(str, [hammingDist(list(seq), r) for r in R]))
      if tag in tags: return False
      tags[tag] = 1
  return True

#Argument is given as a tuple to allow use by map_async
#input: a tuple containing seq and R
#       seq - a sequence of interest
#       R - a set of sequences to determine the distance from to kmer
#return: a string containing the Hamming distances from seq to all elements of R separated by ;
def genTag(args):
  (seq, R) = args
  return ';'.join(map(str, [hammingDist(list(seq), r) for r in R]))

###########################
### CHECK RESOLVABILITY ###
###########################
#Given a set of columns and an object on which to check resolvability, check that the set is resolving
#input: R - a set of columns
#       M - an object on which to check the resolvability of R
#       colNames - optional list of columns. if M is a dictionary of dictionaries and colNames is not empty it will be used as the set of columns to consider, defaults to empty
#       dictDefault - optional default value to use if M is a dictionary of dictionaries, defaults to -1
#return: true if R is resolving and false otherwise
def checkResolving(R, M, colNames=[], dictDefault=-1):
  tags = {}
  elements = []
  if isinstance(M, list) or isinstance(M, np.ndarray): elements = range(len(M))
  elif isinstance(M, dict): elements = M.keys()
  elif isinstance(M, nx.classes.graph.Graph): elements = M.nodes()
  for elem in elements:
    tag = []
    if isinstance(M, list) or isinstance(M, np.ndarray): tag = [M[elem][r] for r in R]
    elif isinstance(M, dict): tag = [M[elem].get(r, dictDefault) for r in R]
    elif isinstance(M, nx.classes.graph.Graph): #tag = [nx.shortest_path_length(M, source=elem, target=r) for r in R]
      for r in R:
        try:
          tag.append(nx.shortest_path_length(M, source=elem, target=r))
        except:
          tag.append(-1)
    tag = ';'.join(map(str, tag))
    if tag in tags: return False
    tags[tag] = 1
  return True






