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
    generate_rgg_with_grid,
    UnitSquareNew
)


def cell_center(i, j, m, n):
    """
    Returns the (x, y) center coordinate of the cell at row i, column j.

    Grid spans [0,1] x [0,1], divided into m rows and n columns.
    """
    x = (j + 0.5) / n
    y = (i + 0.5) / m
    return x, y

def get_nodes_in_cell(grid: dict, row: int, col: int) -> list:
    return grid.get((row, col), [])

def get_metric_dimension_of_graph_with_pruning_igraph_grid(G, r, k_nearest=1):
    g = ig.Graph.from_networkx(G)
    nodes_set = set(range(g.vcount()))
    dist_matrix = g.distances()
    resolving_set = set()
    resolved_nodes = set()
    m = n = math.ceil(1/(2*r))
    d = 1 / max(m, n)
    grid = generate_rgg_with_grid(g,m,n)
    for i in range(m):
      if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix) or not nodes_set:
            break
      for j in range(n):
        if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix) or not nodes_set:
            break
        temp__resolving_set,_,nodes_set = get_metric_dimension_of_unit_square(g,grid,i,j,m,n,r,d,dist_matrix,nodes_set,k_nearest)
        print("Number of nodes added for grid is: "+str(len(temp__resolving_set)))
        resolving_set.update(temp__resolving_set)
        newly_added = list(temp__resolving_set)
        #resolving_set = incremental_global_prune(
         #   g, resolving_set, newly_added, dist_matrix
        #)
    resolving_set = prune_resolving_set_zobrist_fast(g, resolving_set, dist_matrix)
    return resolving_set

def get_metric_dimension_of_unit_square(g, grid, i, j, m, n, r, d, dist_matrix, nodes_set, k_nearest):
    """
    Build a local resolving set for the nodes inside grid cell (i, j).

    The UnitSquareNew generator drives landmark selection: each ideal probe
    point narrows the search to the k_nearest real nodes, from which the
    highest-entropy candidate is chosen.  When the generator is exhausted
    before all nodes are resolved we fall back to a pure entropy-greedy pick
    so the loop always terminates cleanly.  A local Zobrist prune removes
    any redundant landmarks before returning.
    """
    pos = g.vs["pos"]
    nodes_within = get_nodes_in_cell(grid, i, j)
    if not nodes_within:
        return {}, 0, nodes_set

    nodes_set = nodes_set - set(nodes_within)
    resolving_set = set()

    cx, cy = cell_center(i, j, m, n)
    us = UnitSquareNew()
    gen = us.point_generator(cx, cy, r, d)

    nodes_remaining = set(nodes_within)

    while nodes_remaining:
        ideal_point = next(gen, None)

        if ideal_point is not None:
            # Heuristic-guided: find the k nearest nodes to the ideal point,
            # then pick the one with the highest entropy among remaining nodes.
            candidates = sorted(
                nodes_remaining,
                key=lambda v: euclidean_distance(pos[v], ideal_point)
            )[:min(len(nodes_remaining), k_nearest)]
            best = max(
                candidates,
                key=lambda c: entropy_of_landmark_candidate(nodes_remaining, c, dist_matrix)
            )
        else:
            # Generator exhausted before all nodes resolved: fall back to
            # pure entropy-greedy over all remaining nodes.
            best = max(
                nodes_remaining,
                key=lambda c: entropy_of_landmark_candidate(nodes_remaining, c, dist_matrix)
            )

        resolving_set.add(best)
        nodes_remaining.remove(best)

        # Early-exit: check if remaining nodes are already distinguished.
        if nodes_remaining:
            signatures = {
                v: tuple(dist_matrix[v][l] for l in resolving_set)
                for v in nodes_remaining
            }
            if len(signatures) == len(set(signatures.values())):
                break
    return resolving_set, len(resolving_set),nodes_set
    #pruned_local = prune_local_zobrist(list(nodes_within), resolving_set, dist_matrix)
    #return pruned_local, len(pruned_local), nodes_set
