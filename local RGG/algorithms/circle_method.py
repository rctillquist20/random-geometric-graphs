import networkx as nx
import igraph as ig
import numpy as np
import random
import math
import bisect
import heapq
from shapely.geometry import Point, Polygon, box

from functions.resolving_functions import (
    euclidean_distance,
    checkIfResolvingSet_igraph,
    entropy_of_landmark_candidate
)
from functions.zobrist_functions import (
    prune_resolving_set_zobrist_fast
)
from functions.structs import (
    UnitSquare,
    UnitCircle
)


class UnitCircle:
    def __init__(self,center_x,center_y,r):
        self.us = UnitSquare()
        self.centers = []
        self.center_x=center_x
        self.center_y = center_y
        self.r = r
    def add(self):
        coordinate, is_horizontal = self.us.add()
        return self.modifyCenters(coordinate, is_horizontal)

    def modifyCenters(self, coordinate, is_horizontal):
        if not is_horizontal:
            new_x = 0
            if(coordinate>0.5):
              new_x = self.center_x + ((1-coordinate)*2*self.r)
            else:
              new_x = self.center_x + (coordinate*2*self.r)
            self.centers.append((new_x , self.center_y))
            return (new_x, self.center_y)
        else:
            new_y = 0
            if(coordinate>0.5):
                new_y = self.center_y + ((1-coordinate)*2*self.r)
            else:
                new_y = self.center_y + (coordinate*2*self.r)
            self.centers.append((self.center_x, new_y))
            return (self.center_x, new_y)
    def getProbability(self):
        base_circle = Point(self.center_x,self.center_y).buffer(1)
        cut_circles = [Point(x,y).buffer(1) for (x,y) in self.centers]
        regions = [base_circle]
        for cut_circle in cut_circles:
          new_regions = []
          for region in regions:
            inter = region.intersection(cut_circle)
            if not inter.is_empty:
              new_regions.append(inter)
            diff = region.difference(cut_circle)
            if not diff.is_empty:
              new_regions.append(diff)
          regions = new_regions
        total_area = base_circle.area
        area_fractions = [region.area/total_area for region in regions]
        p_same_region = sum(area**2 for area in area_fractions)
        return 1-p_same_region
    def getCenters(self):
      return self.centers
  
def get_metric_dimension_of_graph_with_pruning_igraph_circle(G, r, k_nearest=1, max_iters=1000):
    g = ig.Graph.from_networkx(G)
    nodes_set = set(range(g.vcount()))
    dist_matrix = g.distances()
    resolving_set = set()
    iter_count = 0
    while iter_count < max_iters:
        if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix):
            break
        if not nodes_set:
            break

        degrees = [g.degree(n) for n in nodes_set]
        temp_center = (
            random.choices(list(nodes_set), weights=degrees, k=1)[0]
            if sum(degrees) > 0 else random.choice(list(nodes_set))
        )

        temp_set, _, nodes_set = get_metric_dimension_of_unit_circle_igraph_new(
            g, r, temp_center, dist_matrix, nodes_set,k_nearest)

        resolving_set.update(temp_set)

        newly_added = list(temp_set)
       # resolving_set = incremental_global_prune(
        #    g, resolving_set, newly_added, dist_matrix
        #)

        iter_count += 1

    resolving_set = prune_resolving_set_zobrist_fast(g, resolving_set, dist_matrix)
    return resolving_set

def get_metric_dimension_of_unit_circle_igraph_new(g, r, temp_center, dist_matrix, node_set, k_nearest):
    pos = g.vs["pos"]
    nodes_within = [i for i, d in enumerate(dist_matrix[temp_center]) if i in node_set and d == 1]
    if not nodes_within:
        node_set.remove(temp_center)
        return {temp_center}, 1, node_set
    if temp_center not in nodes_within:
        nodes_within.append(temp_center)
    node_set = node_set - set(nodes_within)
    resolving_set = set()
    x_center, y_center = pos[temp_center]
    uc = UnitCircle(x_center, y_center, r)
    nodes_remaining = set(nodes_within)
    while nodes_remaining:
        ideal_point = uc.add()
        candidates = sorted(
            nodes_remaining,
            key=lambda v: euclidean_distance(pos[v], ideal_point)
        )[:min(len(nodes_remaining),k_nearest)]
        best = max(candidates, key=lambda c: entropy_of_landmark_candidate(nodes_remaining, c, dist_matrix))
        resolving_set.add(best)
        nodes_remaining.remove(best)
        signatures = {}
        for v in nodes_remaining:
            sig = tuple(dist_matrix[v][l] for l in resolving_set)
            signatures[v] = sig
        if len(signatures) == len(set(signatures.values())):
            break
    return resolving_set, len(resolving_set), node_set
    #pruned_local = prune_local_zobrist(list(nodes_within), resolving_set, dist_matrix)

    #return pruned_local, len(pruned_local), node_set