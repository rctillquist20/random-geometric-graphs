#Python code to collect data related to the metric dimension of random geometric graphs

import numpy as np
import networkx as nx
from multilateration import ich
from itertools import product
import multiprocessing as mp
import pickle
import glob

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

#determines the number of additional repeats necessary for each n,r pair in pairs
#input: data - a list of tuples (n, r, seed, resSet)
#       pairs - a list of tuples (n, r) to consider
#       repeats - the target number of repeats for each (n,r) pair
#return a dictionary (n,r)->(repeats - number of occurences in data)
def countComplete(data, pairs, repeats):
  counts = {pair: repeats for pair in pairs}
  for (n, r, _, _) in data:
    if (n,r) in counts: counts[(n,r)] -= 1
  return counts

if __name__=='__main__':
  dataFile = 'rgg_data.list'
  data = readList(dataFile) if glob.glob(dataFile) else []

  nList = [100, 200] #list(range(100, 1001, 100)) + [2000, 5000] #to start consider smaller values
  rList = [0.02, 0.1, 0.5, 1, np.sqrt(2)] #list(np.arange(0.02, 0.14, 0.01)) + list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))
  repeats = 2 #we can increase this later

  #loop over all pairs of n and r (this can be done with nested loops or the product function in itertools)
  #look through data to see how many more repeats we need of this n,r pair (repeats-(the number in data))
  #..the countComplete function might help here
  #use np.random.randint(1, 1000000, size=(the number of additional repeats required)) to generate seeds
  #use these seeds to generate random graphs, nx.random_geometric_graph(n, r, seed=seed)
  #use the ich function to find a small resolving set
  #append (n, r, seed, resolving set) to data
  #save data

  print('Done')

