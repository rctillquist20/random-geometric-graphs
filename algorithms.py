#Python code implementing algorithms for finding small resolving sets of RGGs efficiently

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from multilateration import checkResolving, ich
from dataCollection import readList, writeFile
import glob
import time
from collections import Counter

#select nodes from G one at a time uniformly at random until a resolving set is created
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

#consider components separetely
#remove isolated nodes and components of size 2
#run ich on all other
def ichComponents(G):
  R = []
  iso = False
#  components = sorted([c for c in nx.connected_components(G)], key=len)
  components = [c for c in nx.connected_components(G)]
  for i,H in enumerate(components):
    if len(H) == 1 and not iso: iso = True
    elif len(H) == 1 and iso: R.append(next(iter(H)))
#    if len(H) == 1 and i > 0: R.append(next(iter(H)))
    elif len(H) == 2: R.append(next(iter(H))) #list(H)[0]
    else: R.extend([sorted(list(H))[r] for r in ich(G.subgraph(H))]) #i > 0
  return R

#farthest first traversal - pick ...

#start with a random node
#pick subsequent nodes with some fraction of radius offset in different directions

#given a number of nodes, pick so that distances are offset in each direction

#grid...

#run a given algorithm on all graphs in a data set
#collect resolving sets and times to compare against other approaches
def runAlgorithm(algo, data):
  results = []
  for i,(n, r, seed, resSet, t) in enumerate(data):
    if i%10==0: print('completed', i/len(data))
    G = nx.random_geometric_graph(n, r, seed=seed)
    start = time.time()
    R = algo(G)
    end = time.time()
    if not checkResolving(R, G):
      print('ERROR', sorted(R), len(R))
      print('.....', sorted(resSet), len(resSet))
      break
    results.append((n,r,seed,R,end-start))
  return results

#plot the difference in resolving set size and times for a set of data
def plotDiffs(ichInfo, algoInfo):
  matched = {}
  for (n,r,seed,resSet,t) in ichInfo:
    if (n,r,seed) not in matched: matched[(n,r,seed)] = {'ich':[], 'algo':[]}
    matched[(n,r,seed)]['ich'] += [len(resSet), t]
  for (n,r,seed,resSet,t) in algoInfo:
    if (n,r,seed) not in matched: matched[(n,r,seed)] = {'ich':[], 'algo':[]}
    matched[(n,r,seed)]['algo'] += [len(resSet), t]
  resSetDiffs = [matched[combo]['ich'][0] - matched[combo]['algo'][0] for combo in matched]
  timeDiffs = [matched[combo]['ich'][1] - matched[combo]['algo'][1] for combo in matched]

  print('res set diff counts', Counter(resSetDiffs))
#  print('time diff counts', Counter(timeDiffs))

  plt.hist(resSetDiffs, alpha=0.5, density=True)
  plt.title('Resolving Set Size Differences')
  plt.xlabel('Difference (ICH - algo)')
  plt.ylabel('Frequency')
  plt.show()

  plt.hist(timeDiffs, alpha=0.5, density=True)
  plt.title('Runtime Differences')
  plt.xlabel('Difference (ICH - algo)')
  plt.ylabel('Frequency')
  plt.show()

#
def saveResults(data, algo=ichComponents, saveFile=''):
  if not saveFile: saveFile = 'rgg_ichComponents_2.list'
  results = readList(saveFile) if glob.glob(saveFile) else []

  complete = set([(n,r,seed) for (n,r,seed,_,_) in results])
  jobs = [(n,r,seed,resSet,t) for (n,r,seed,resSet,t) in data if (n,r,seed) not in complete]

  for i,(n,r,seed,resSet,t) in enumerate(jobs):
    print(i, len(jobs), i/len(jobs), n, r)
    G = nx.random_geometric_graph(n, r, seed=seed)
    start = time.time()
    R = algo(G)
    end = time.time()
    results.append((n,r,seed,R,end-start))
    if not checkResolving(R, G):
      print('ERROR', sorted(R), len(R))
      print('.....', sorted(resSet), len(resSet))
      break
    if end-start > 100 or i%10==0:
      print('writing')
      writeFile(results, saveFile)

  if len(data)>0:
    print('writing')
    writeFile(results, saveFile)

  return results

#
if __name__=='__main__':
  dataFile = 'rgg_data_2.list'
  data = readList(dataFile) if glob.glob(dataFile) else []

  data = [values for values in data if values[1] <= np.sqrt(np.log(values[0])/(np.pi*values[0]))]# and values[0] <= 100]
  results = saveResults(data)
  print('DONE')
  #exit(0) #remove
#  results = runAlgorithm(randomSet, data)
#  results = runAlgorithm(ichComponents, data)
  for (n,r,seed,R,t) in sorted(results): print(n,r,len(R),t)
  rad = np.random.choice([v for (_,v,_,_,_) in data])
  print('radius', rad)
  print('ICH', np.mean([len(R) for (_,r,_,R,_) in data if r==rad]), 'Algo', np.mean([len(R) for (_,r,_,R,_) in results if r==rad]))

  plotDiffs(data, results)
  
