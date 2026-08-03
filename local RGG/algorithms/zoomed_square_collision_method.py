"""Isolated Zoomed Square experiment for entropy versus collision scoring.

The existing :mod:`zoomed_square_method` is intentionally left unchanged.
Both selectors in this module share the same center selection, one-hop
neighborhoods, probe generation, candidate pools, stopping rules, and final
pruning so the local candidate score is the controlled difference.
"""

from dataclasses import dataclass
import random

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
from functions.structs import UnitSquareNew
from functions.zobrist_functions import prune_resolving_set_zobrist_fast


@dataclass(frozen=True)
class ZoomedSquareSelectionRun:
    """Resolving set plus its size before the shared pruning stage."""

    resolving_set: set[int]
    pre_prune_size: int


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


def _resolve_zoomed_neighborhood(
    g,
    radius,
    center,
    dist_matrix,
    nodes_set,
    k_nearest,
    strategy,
):
    positions = g.vs["pos"]
    nodes_within = [
        node
        for node, distance in enumerate(dist_matrix[center])
        if node in nodes_set and distance == 1
    ]

    if not nodes_within:
        nodes_set.remove(center)
        return {center}, nodes_set

    nodes_within.append(center)
    nodes_set = nodes_set - set(nodes_within)
    nodes_remaining = set(nodes_within)
    resolving_set = set()
    current_signature_classes = {node: 0 for node in nodes_remaining}

    generator = UnitSquareNew().point_generator(
        positions[center][0],
        positions[center][1],
        radius,
        2 * radius,
    )

    while nodes_remaining:
        ideal_point = next(generator, None)
        if ideal_point is None:
            candidates = nodes_remaining
        else:
            candidates = sorted(
                nodes_remaining,
                key=lambda node: euclidean_distance(
                    positions[node],
                    ideal_point,
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


def _run_zoomed_square_selector(
    graph,
    radius,
    k_nearest,
    strategy,
    max_iters,
):
    if radius <= 0:
        raise ValueError("radius must be positive")
    if k_nearest < 1:
        raise ValueError("k_nearest must be at least 1")
    if max_iters < 1:
        raise ValueError("max_iters must be at least 1")

    g = ig.Graph.from_networkx(graph)
    dist_matrix = g.distances()
    nodes_set = set(range(g.vcount()))
    resolving_set = set()
    iter_count = 0

    while iter_count < max_iters:
        if checkIfResolvingSet_igraph(g, resolving_set, dist_matrix):
            break
        if not nodes_set:
            break

        degrees = [g.degree(node) for node in nodes_set]
        center = (
            random.choices(list(nodes_set), weights=degrees, k=1)[0]
            if sum(degrees) > 0
            else random.choice(list(nodes_set))
        )
        local_set, nodes_set = _resolve_zoomed_neighborhood(
            g,
            radius,
            center,
            dist_matrix,
            nodes_set,
            k_nearest,
            strategy,
        )
        resolving_set.update(local_set)
        iter_count += 1

    pre_prune_size = len(resolving_set)
    resolving_set = prune_resolving_set_zobrist_fast(
        g,
        resolving_set,
        dist_matrix,
    )
    return ZoomedSquareSelectionRun(resolving_set, pre_prune_size)


def get_metric_dimension_zoomed_square_entropy_experimental(
    graph,
    radius,
    k_nearest=5,
    max_iters=1000,
):
    """Run the isolated Zoomed Square control with entropy scoring."""

    return _run_zoomed_square_selector(
        graph,
        radius,
        k_nearest,
        "entropy",
        max_iters,
    )


def get_metric_dimension_zoomed_square_collision(
    graph,
    radius,
    k_nearest=5,
    max_iters=1000,
):
    """Run Zoomed Square with collision-minimizing candidate selection."""

    return _run_zoomed_square_selector(
        graph,
        radius,
        k_nearest,
        "collision",
        max_iters,
    )
