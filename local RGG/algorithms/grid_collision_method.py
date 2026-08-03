"""Isolated grid experiment comparing entropy and collision landmark scores.

This module deliberately does not alter ``grid_method.py``. Both experimental
selectors run through the same traversal, probe generation, early-exit, and
pruning code here so the scoring rule is the only controlled difference.
"""

from dataclasses import dataclass
import math

import igraph as ig

from functions.collision_functions import (
    count_colliding_pairs,
    extend_signatures,
    select_collision_minimizing_candidate,
)
from functions.resolving_functions import (
    checkIfResolvingSet_igraph,
    entropy_of_landmark_candidate,
    euclidean_distance,
)
from functions.structs import UnitSquareNew, generate_rgg_with_grid
from functions.zobrist_functions import prune_resolving_set_zobrist_fast


@dataclass(frozen=True)
class GridSelectionRun:
    """Result and basic diagnostics from one experimental grid run."""

    resolving_set: set[int]
    pre_prune_size: int


def _cell_center(row: int, column: int, rows: int, columns: int):
    return (column + 0.5) / columns, (row + 0.5) / rows


def _select_candidate(
    strategy,
    nodes_remaining,
    candidates,
    current_signature_classes,
    dist_matrix,
):
    if strategy == "entropy":
        return max(
            candidates,
            key=lambda candidate: entropy_of_landmark_candidate(
                nodes_remaining,
                candidate,
                dist_matrix,
            ),
        )
    if strategy == "collision":
        return select_collision_minimizing_candidate(
            nodes_remaining,
            candidates,
            current_signature_classes,
            dist_matrix,
        )
    raise ValueError(f"unknown selection strategy: {strategy}")


def _resolve_grid_cell(
    g,
    grid,
    row,
    column,
    rows,
    columns,
    radius,
    step_size,
    dist_matrix,
    nodes_set,
    k_nearest,
    strategy,
):
    positions = g.vs["pos"]
    nodes_within = grid.get((row, column), [])
    if not nodes_within:
        return set(), nodes_set

    nodes_set = nodes_set - set(nodes_within)
    nodes_remaining = set(nodes_within)
    resolving_set = set()
    current_signature_classes = {node: 0 for node in nodes_remaining}

    center_x, center_y = _cell_center(row, column, rows, columns)
    generator = UnitSquareNew().point_generator(
        center_x,
        center_y,
        radius,
        step_size,
    )

    while nodes_remaining:
        ideal_point = next(generator, None)

        if ideal_point is None:
            candidates = sorted(nodes_remaining)
        else:
            candidates = sorted(
                nodes_remaining,
                key=lambda node: (
                    euclidean_distance(positions[node], ideal_point),
                    node,
                ),
            )[: min(len(nodes_remaining), k_nearest)]

        best = _select_candidate(
            strategy,
            nodes_remaining,
            candidates,
            current_signature_classes,
            dist_matrix,
        )

        current_signature_classes = extend_signatures(
            nodes_remaining,
            best,
            current_signature_classes,
            dist_matrix,
        )
        resolving_set.add(best)
        nodes_remaining.remove(best)
        current_signature_classes.pop(best, None)

        if (
            not nodes_remaining
            or count_colliding_pairs(current_signature_classes) == 0
        ):
            break

    return resolving_set, nodes_set


def _run_grid_selector(G, radius, k_nearest, strategy):
    if radius <= 0:
        raise ValueError("radius must be positive")
    if k_nearest < 1:
        raise ValueError("k_nearest must be at least 1")

    g = ig.Graph.from_networkx(G)
    dist_matrix = g.distances()
    nodes_set = set(range(g.vcount()))
    resolving_set = set()

    rows = columns = math.ceil(1 / (2 * radius))
    step_size = 1 / max(rows, columns)
    grid = generate_rgg_with_grid(g, rows, columns)

    for row in range(rows):
        if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix) or not nodes_set:
            break
        for column in range(columns):
            if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix) or not nodes_set:
                break
            local_set, nodes_set = _resolve_grid_cell(
                g,
                grid,
                row,
                column,
                rows,
                columns,
                radius,
                step_size,
                dist_matrix,
                nodes_set,
                k_nearest,
                strategy,
            )
            resolving_set.update(local_set)

    pre_prune_size = len(resolving_set)
    resolving_set = prune_resolving_set_zobrist_fast(
        g,
        resolving_set,
        dist_matrix,
    )
    return GridSelectionRun(resolving_set, pre_prune_size)


def get_metric_dimension_grid_entropy_experimental(G, radius, k_nearest=5):
    """Run the isolated grid control using the existing entropy score."""
    return _run_grid_selector(G, radius, k_nearest, "entropy")


def get_metric_dimension_grid_collision(G, radius, k_nearest=5):
    """Run the isolated grid variant that minimizes signature collisions."""
    return _run_grid_selector(G, radius, k_nearest, "collision")
