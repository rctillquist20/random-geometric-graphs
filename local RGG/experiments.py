#clean up 
#collect data for presentation figures.... useful for paper and more...

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely import intersection, intersection_all, difference, set_precision
import matplotlib.pyplot as plt
from itertools import product, repeat
from jax.random import ball, key, split
import pickle
import glob
import time

##################
### READ/WRITE ###
##################
def readDict(inFile):
  d = {}
  with open(inFile, 'rb') as f:
    d = pickle.load(f)
  return d

def writeFile(data, outFile):
  with open(outFile, 'wb') as o:
    pickle.dump(data, o, protocol=pickle.HIGHEST_PROTOCOL)

#generate n random points in the unit circle in Lp space of given dimension
def randUnitCircle(n=1, p=2, dim=2, k=key(123)):
  if p==np.inf: return np.random.uniform(-1, 1, size=(n, dim)).tolist()
  points = []
  for _ in range(n):
    k, b = split(k)
    points.append(ball(b, dim, p=p))
  return points

#calculate the probability of a collision given region areas
def collisionProb(areas):
  denom = sum(areas)**2
  return sum(a*a/denom for a in areas)

def getAreas(points, p=2, quad_segs=32):
  base = makeCircle((0, 0), p=p, quad_segs=quad_segs)
  circles = [makeCircle(point, p=p, quad_segs=quad_segs) for point in points]
  regions = [[[], base]]
  for circle in circles:
    nextRegions = []
    for dists,region in regions:
      A = intersection(region, circle)
      B = difference(region, circle)
      if not A.is_empty: nextRegions.append([dists+[1], A])
      if not B.is_empty: nextRegions.append([dists+[2], B])
    regions = nextRegions
  return {tuple(dist): region.area for dist,region in regions}

#generate a shapely unit circle centered at the given point in Lp space
#for p not in [1, 2, infinity], the circle is approximated with the given number of randomly placed vertices
def makeCircle(point, p=2, vertices=100, quad_segs=16):
  x, y = point
  if p==1: return Polygon([(x+xt, y+yt) for (xt, yt) in [(0,-1), (1,0), (0,1), (-1,0)]])
  if p==2: return Point(x, y).buffer(1, quad_segs=quad_segs)
  if p==np.inf: return Polygon([(x+xt, y+yt) for (xt, yt) in [(1,1), (-1,1), (-1,-1), (1,-1)]])

  return Polygon([tuple([x/np.linalg.norm(vec, ord=p) for x in vec]) for vec in randUnitCircle(n=vertices, p=p)])

def collectData(nList, pList, repeats=1, quad_segs=16, fileName=''):
  data = {p:{n: [] for n in nList} for p in pList}
  for p in pList:
    print('p', p)
    for n in nList:
      print('...n', n)
      for rep in range(repeats):
        points = randUnitCircle(n=n, p=p, k=key(np.random.randint(0, 10000)))
        areas = getAreas(points, p=p, quad_segs=quad_segs)
        data[p][n].append(list(areas.values()))
  if fileName: writeFile(data, fileName)
  return data

def plotCollisionProbsVSN(data, p=2):
  X = sorted(list(data[p].keys()))
  Y = [np.mean([collisionProb(a) for a in data[p][x]]) for x in X]
  E = [np.std([collisionProb(a) for a in data[p][x]]) for x in X]
  plt.errorbar(X, Y, yerr=E)
#  plt.plot(X, [256/(x+8)**2 for x in X], 'r-', label='upper')
#  plt.plot(X, [64/(x+1)**2 for x in X], 'g-', label='lower')
  plt.show()

def plotCollisionProbs(data, n=1, p=2):
  probs = [collisionProb(regions) for regions in data[p][n]]
  plt.hist(probs, bins=50)
  plt.show()

if __name__=='__main__':
  outFile = 'local_continuous_data.dict'
#  outFile = 'local_continuous_data_one_point.dict'
  nList = [1]+list(range(5, 76, 5))#[1,5,10,20] #range(1, 20, 3)...
  pList = [1, 2, np.inf]
  repeats = 50
  quad_segs = 1024

  data = collectData(nList, pList, repeats=repeats, quad_segs=quad_segs, fileName=outFile)

  for p in pList: plotCollisionProbsVSN(data, p=p)
  for p in pList: plotCollisionProbs(data, n=1, p=p)

  print('DONE')
