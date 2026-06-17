import networkx as nx
import igraph as ig
import numpy as np
import math

from functions.resolving_functions import (
    euclidean_distance,
    checkIfResolvingSet_igraph,
    entropy_of_landmark_candidate
)
from functions.zobrist_functions import (
    prune_resolving_set_zobrist_fast
)

def get_metric_dimension_of_graph_with_pruning_igraph_zoomed_square(G, r, k_nearest=1, max_iters=1000):
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

        temp_set, _, nodes_set = get_metric_dimension_of_unit_square_zoomed_square(
            g, r, temp_center, dist_matrix, nodes_set, k_nearest)

        resolving_set.update(temp_set)
        iter_count += 1

    resolving_set = prune_resolving_set_zobrist_fast(g, resolving_set, dist_matrix)
    return resolving_set

def get_metric_dimension_of_unit_square_zoomed_square(g, r, temp_center, dist_matrix, nodes_set, k_nearest):
    """
    Build a local resolving set for the nodes within graph distance 1 of
    temp_center, using the UnitSquareNew heuristic to guide probe point
    selection. Falls back to entropy-greedy when the generator is exhausted.
    """
    pos = g.vs["pos"]
    nodes_within = [i for i, d in enumerate(dist_matrix[temp_center]) if i in nodes_set and d == 1]
    if not nodes_within:
        nodes_set.remove(temp_center)
        return {temp_center}, 1, nodes_set
    if temp_center not in nodes_within:
        nodes_within.append(temp_center)
    nodes_set = nodes_set - set(nodes_within)
    resolving_set = set()

    x_center, y_center = pos[temp_center]
    us = UnitSquareNew()
    d = 2 * r
    gen = us.point_generator(x_center, y_center, r, d)

    nodes_remaining = set(nodes_within)

    while nodes_remaining:
        ideal_point = next(gen, None)

        if ideal_point is not None:
            candidates = sorted(
                nodes_remaining,
                key=lambda v: euclidean_distance(pos[v], ideal_point)
            )[:min(len(nodes_remaining), k_nearest)]
            best = max(
                candidates,
                key=lambda c: entropy_of_landmark_candidate(nodes_remaining, c, dist_matrix)
            )
        else:
            best = max(
                nodes_remaining,
                key=lambda c: entropy_of_landmark_candidate(nodes_remaining, c, dist_matrix)
            )

        resolving_set.add(best)
        nodes_remaining.remove(best)

        if nodes_remaining:
            signatures = {
                v: tuple(dist_matrix[v][l] for l in resolving_set)
                for v in nodes_remaining
            }
            if len(signatures) == len(set(signatures.values())):
                break

    return resolving_set, len(resolving_set), nodes_set