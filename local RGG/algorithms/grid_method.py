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

def generate_rgg_with_grid(G, m, n):
    grid = {(r, c): [] for r in range(m) for c in range(n)}
    pos = {}

    for node in range(G.vcount()):
        coord = G.vs[node]["pos"]
        x, y = coord[0], coord[1]

        pos[node] = (x, y)

        col = min(int(x * n), n - 1)
        row = min(int(y * m), m - 1)
        grid[(row, col)].append(node)

    return grid

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
