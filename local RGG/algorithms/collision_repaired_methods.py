"""Post-repaired wrappers around the isolated collision-based methods."""

from dataclasses import dataclass

import igraph as ig

from algorithms.circle_collision_method import (
    get_metric_dimension_circle_collision,
)
from algorithms.grid_collision_method import get_metric_dimension_grid_collision
from algorithms.ich_collision_method import get_metric_dimension_ich_collision
from algorithms.zoomed_square_collision_method import (
    get_metric_dimension_zoomed_square_collision,
)
from functions.global_collision_repair import repair_resolving_set_globally


@dataclass(frozen=True)
class CollisionRepairedMethodRun:
    """Common result record for a collision method followed by global repair."""

    resolving_set: set[int]
    original_method_pre_prune_size: int
    original_size: int
    repaired_pre_prune_size: int
    repair_probes: tuple[int, ...]
    collision_pairs_before: int
    collision_pairs_after: int
    pruned_after_repair: int


def _combine_run(method_run, repair_run):
    return CollisionRepairedMethodRun(
        resolving_set=repair_run.resolving_set,
        original_method_pre_prune_size=method_run.pre_prune_size,
        original_size=repair_run.original_size,
        repaired_pre_prune_size=repair_run.repaired_pre_prune_size,
        repair_probes=repair_run.repair_probes,
        collision_pairs_before=repair_run.collision_pairs_before,
        collision_pairs_after=repair_run.collision_pairs_after,
        pruned_after_repair=repair_run.pruned_after_repair,
    )


def _repair_geometric_run(graph, method_run):
    converted = ig.Graph.from_networkx(graph)
    repaired = repair_resolving_set_globally(
        converted,
        method_run.resolving_set,
    )
    return _combine_run(method_run, repaired)


def _igraph_in_sorted_networkx_order(graph):
    """Match the sorted-node indexing used by the isolated ICH selector."""

    ordered_nodes = sorted(graph.nodes())
    node_ids = {node: index for index, node in enumerate(ordered_nodes)}
    edges = [
        (node_ids[source], node_ids[target])
        for source, target in graph.edges()
    ]
    return ig.Graph(
        n=len(ordered_nodes),
        edges=edges,
        directed=graph.is_directed(),
    )


def get_metric_dimension_grid_collision_repaired(
    graph,
    radius,
    k_nearest=5,
):
    """Run Grid Collision and repair any remaining global collisions."""

    method_run = get_metric_dimension_grid_collision(
        graph,
        radius,
        k_nearest=k_nearest,
    )
    return _repair_geometric_run(graph, method_run)


def get_metric_dimension_circle_collision_repaired(
    graph,
    radius,
    k_nearest=5,
    max_iters=1000,
):
    """Run Circle Collision and repair any remaining global collisions."""

    method_run = get_metric_dimension_circle_collision(
        graph,
        radius,
        k_nearest=k_nearest,
        max_iters=max_iters,
    )
    return _repair_geometric_run(graph, method_run)


def get_metric_dimension_zoomed_square_collision_repaired(
    graph,
    radius,
    k_nearest=5,
    max_iters=1000,
):
    """Run Zoomed Square Collision, then repair global collisions."""

    method_run = get_metric_dimension_zoomed_square_collision(
        graph,
        radius,
        k_nearest=k_nearest,
        max_iters=max_iters,
    )
    return _repair_geometric_run(graph, method_run)


def get_metric_dimension_ich_collision_repaired(
    graph,
    rand_order=True,
):
    """Run ICH Collision and repair any remaining global collisions."""

    method_run = get_metric_dimension_ich_collision(
        graph,
        rand_order=rand_order,
    )
    converted = _igraph_in_sorted_networkx_order(graph)
    repaired = repair_resolving_set_globally(
        converted,
        method_run.resolving_set,
    )
    return _combine_run(method_run, repaired)
