#Python code to explore data collected related to random geometric graphs

import numpy as np
import matplotlib.pyplot as plt
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

#read all files in same directory with .list suffix
def readAllData():
  data = []
  for f in glob.glob('*.list'):
    data.extend(readList(f))
  return data

#############
### PLOTS ###
#############
#for a fixed value of n, plot radius vs metric dimension
def plotRadiusVSDim(data, plotN):
  info = {}
  for (r, dim) in [(r, len(resSet)) for (n, r, _, resSet, _) in data if n==plotN]:
    info[r] = info.get(r, []) + [dim]
  X = sorted(info.keys())
  Y = [np.mean(info[r]) for r in X]
  E = [np.std(info[r]) for r in X]
  thresh = np.sqrt(np.log(plotN) / (np.pi*plotN))
  plt.plot([thresh, thresh], [0, plotN], 'k--', alpha=0.5, label='Connectivity Threshold')
  plt.errorbar(X, Y, yerr=E, alpha=0.5, capsize=1)
  plt.title(r'Radius vs Metric Dimension $(n='+str(plotN)+')$')
  plt.xlabel('Radius')
  plt.ylabel('Metric Dimension')
  plt.show()

#for a fixed radius, plot n vs metric dimension
def plotNVSDim(data, plotR):
  info = {}
  for (n, dim) in [(n, len(resSet)) for (n, r, _, resSet, _) in data if np.isclose(r, plotR)]:
    info[n] = info.get(n, []) + [dim]
  X = sorted(info.keys())
  Y = [np.mean(info[n]) for n in X]
  E = [np.std(info[n]) for n in X]
  plt.errorbar(X, Y, yerr=E, alpha=0.5, capsize=2)
  plt.title(r'Nodes vs Metric Dimension $(r='+str(plotR)+')$')
  plt.xlabel('n')
  plt.ylabel('Metric Dimension')
  plt.show()

#for a fixed n, plot the number of edges vs metric dimension (will require remaking the graph)
#plot the number of edges vs metric dimension for all n (will require remaking the graph)
#plot ich run time vs metric dimension
#plot distance between closes elements of resolving sets (will require remaking the graph)
#...

#
if __name__=='__main__':
  data = readAllData()

  plotRadiusVSDim(data, 500)
  plotNVSDim(data, 0.04)



