"""Isolated ICH experiment comparing entropy and collision objectives.

The existing :mod:`ich_multilateration` implementation is not modified.  Both
selectors here use the same distance matrix, randomized candidate order,
signature updates, and stopping rule; only the candidate score differs.
"""

from collections import Counter
from dataclasses import dataclass
import math

import networkx as nx
import numpy as np

from functions.collision_functions import (
    count_colliding_pairs,
    distance_code,
    extend_signatures,
)


@dataclass(frozen=True)
class ICHSelectionRun:
    """Final resolving set and the order in which landmarks were selected."""

    resolving_set: set[int]
    pre_prune_size: int
    selection_order: tuple[int, ...]


def _distance_matrix(graph):
    nodes = sorted(graph.nodes())
    distances = dict(nx.floyd_warshall(graph))
    return [
        [
            int(distances[source][target])
            if distances[source][target] != float("inf")
            else -1
            for target in nodes
        ]
        for source in nodes
    ]


def _refined_counts(nodes, candidate, signature_classes, dist_matrix):
    return Counter(
        (
            signature_classes[node],
            distance_code(dist_matrix[node][candidate]),
        )
        for node in nodes
    )


def _entropy_score(counts):
    total = sum(counts.values())
    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
    )


def _collision_score(counts):
    return sum(count * (count - 1) // 2 for count in counts.values())


def _run_ich_selector(graph, strategy, rand_order):
    if strategy not in {"entropy", "collision"}:
        raise ValueError(f"unknown selection strategy: {strategy}")

    dist_matrix = _distance_matrix(graph)
    node_count = len(dist_matrix)
    nodes = tuple(range(node_count))
    signature_classes = {node: 0 for node in nodes}
    candidates = list(nodes)
    if rand_order:
        candidates = list(np.random.permutation(candidates))

    chosen = []
    while count_colliding_pairs(signature_classes) > 0 and candidates:
        best_candidate = None
        best_score = None

        for candidate in candidates:
            counts = _refined_counts(
                nodes,
                candidate,
                signature_classes,
                dist_matrix,
            )
            score = (
                _entropy_score(counts)
                if strategy == "entropy"
                else _collision_score(counts)
            )
            if (
                best_candidate is None
                or (strategy == "entropy" and score > best_score)
                or (strategy == "collision" and score < best_score)
            ):
                best_candidate = candidate
                best_score = score

        signature_classes = extend_signatures(
            nodes,
            best_candidate,
            signature_classes,
            dist_matrix,
        )
        chosen.append(best_candidate)
        candidates.remove(best_candidate)

    return ICHSelectionRun(set(chosen), len(chosen), tuple(chosen))


def get_metric_dimension_ich_entropy_experimental(graph, rand_order=True):
    """Run a controlled reproduction of the existing entropy-based ICH."""

    return _run_ich_selector(graph, "entropy", rand_order)


def get_metric_dimension_ich_collision(graph, rand_order=True):
    """Run ICH using remaining colliding node pairs as the objective."""

    return _run_ich_selector(graph, "collision", rand_order)
