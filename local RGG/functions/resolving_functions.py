import math
import numpy as np
from collections import Counter

def euclidean_distance(p, q):
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)

def checkIfResolvingSet_igraph(g, S, dist_matrix):
    if not S:
        return False
    nodes = list(range(g.vcount()))
    representations = {}
    for v in nodes:
        rep = tuple(dist_matrix[s][v] for s in S)
        if rep in representations:
            return False
        representations[rep] = v
    return True

def entropy_of_landmark_candidate(nodes, candidate, dist_matrix):
    cnt = Counter()
    for v in nodes:
        d = dist_matrix[v][candidate]
        code = int(d) if d < float('inf') else -1
        cnt[code] += 1
    total = sum(cnt.values())
    H = 0.0
    for c in cnt.values():
        p = c / total
        H -= p * math.log2(p)
    return H

