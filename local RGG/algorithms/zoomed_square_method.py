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

class UnitSquareNew:
    """
    Heuristic point generator for the grid-based metric dimension algorithm.

    The two fitted curves (defined in the canonical frame centered at (cx, cy))
    are:
        curve1: y = -0.028964*(x-cx)^2 + 0.985804*(x-cx) + 0.630070 + cy
        curve2: y =  0.021721*(x-cx)^2 + 0.981117*(x-cx) - 0.626609 + cy

    point_generator yields ideal probe points in the order dictated by the
    pattern in pattern.pdf:
      1. Center of curve1 (x=cx), then center of curve2 (x=cx).
      2. Expand symmetrically left/right in steps of d, yielding
         (x+d, curve1), (x+d, curve2), (x-d, curve1), (x-d, curve2), ...
      A point is only yielded if it falls inside the grid cell's bounding
      square [cx-r, cx+r] x [cy-r, cy+r].  The generator stops once a full
      expansion step produces no in-bounds points on either curve in either
      direction.

    Yields: (x, y) tuples (curve_id dropped; callers only need coordinates).
    """

    @staticmethod
    def _curve1_y(x, cx, cy):
        dx = x - cx
        return -0.028964 * dx**2 + 0.985804 * dx + 0.630070 + cy

    @staticmethod
    def _curve2_y(x, cx, cy):
        dx = x - cx
        return  0.021721 * dx**2 + 0.981117 * dx - 0.626609 + cy

    @staticmethod
    def _in_square(x, y, cx, cy, r):
        """True iff (x, y) is inside the axis-aligned cell square of half-side r."""
        return (cx - r) <= x <= (cx + r) and (cy - r) <= y <= (cy + r)

    def point_generator(self, cx, cy, r, d):
        """
        Generator of ideal probe points for the cell centred at (cx, cy).

        Parameters
        ----------
        cx, cy : float  -- cell centre in RGG [0,1]^2 space
        r      : float  -- RGG radius (half-side of the grid cell)
        d      : float  -- step size along x between successive probe points
        """
        # --- Step 0: centre points (x = cx) ---
        y1_center = self._curve1_y(cx, cx, cy)
        if self._in_square(cx, y1_center, cx, cy, r):
            yield (cx, y1_center)

        y2_center = self._curve2_y(cx, cx, cy)
        if self._in_square(cx, y2_center, cx, cy, r):
            yield (cx, y2_center)

        # --- Steps 1, 2, 3, ...: expand symmetrically ---
        step = 1
        while True:
            any_yielded = False

            for sign in [1, -1]:
                x = cx + sign * step * d

                y1 = self._curve1_y(x, cx, cy)
                if self._in_square(x, y1, cx, cy, r):
                    yield (x, y1)
                    any_yielded = True

                y2 = self._curve2_y(x, cx, cy)
                if self._in_square(x, y2, cx, cy, r):
                    yield (x, y2)
                    any_yielded = True

            if not any_yielded:
                return

            step += 1

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