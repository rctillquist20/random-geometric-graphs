"""Deterministically repair unresolved global distance-signature collisions."""

from dataclasses import dataclass
from numbers import Integral

from functions.collision_functions import (
    collision_score_of_landmark_candidate,
    count_colliding_pairs,
    extend_signatures,
)
from functions.zobrist_functions import prune_resolving_set_zobrist_fast


@dataclass(frozen=True)
class GlobalRepairRun:
    """Result and diagnostics from an exact global collision repair."""

    resolving_set: set[int]
    original_size: int
    repaired_pre_prune_size: int
    repair_probes: tuple[int, ...]
    collision_pairs_before: int
    collision_pairs_after: int
    pruned_after_repair: int


def _normalized_distance_matrix(g, dist_matrix):
    node_count = g.vcount()
    source = g.distances() if dist_matrix is None else dist_matrix

    if len(source) != node_count or any(
        len(row) != node_count for row in source
    ):
        raise ValueError("dist_matrix must be square with one row per vertex")

    # Some project methods represent an unreachable distance as -1, while
    # igraph uses infinity. Normalize the former so the pruning implementation
    # also treats disconnected vertices consistently.
    return [
        [float("inf") if distance < 0 else distance for distance in row]
        for row in source
    ]


def _global_signature_classes(node_count, landmarks, dist_matrix):
    nodes = tuple(range(node_count))
    signature_classes = {node: 0 for node in nodes}
    for landmark in sorted(landmarks):
        signature_classes = extend_signatures(
            nodes,
            landmark,
            signature_classes,
            dist_matrix,
        )
    return signature_classes


def _exact_collision_pairs(node_count, landmarks, dist_matrix):
    return count_colliding_pairs(
        _global_signature_classes(node_count, landmarks, dist_matrix)
    )


def _is_resolving_by_project_convention(
    node_count,
    resolving_set,
    collision_pairs,
):
    # The project's resolver check requires a nonempty landmark set whenever
    # the graph has vertices. In particular, a singleton therefore needs its
    # sole vertex even though there are no unordered vertex pairs to collide.
    return collision_pairs == 0 and (node_count == 0 or bool(resolving_set))


def repair_resolving_set_globally(g, resolving_set, dist_matrix=None):
    """Add globally useful probes until every vertex signature is unique.

    Candidates are scored against all graph vertices, not only the local
    neighborhood that selected the original probes. The candidate leaving the
    fewest unordered colliding pairs is chosen at each step, with the lowest
    vertex ID as the deterministic tie-breaker.

    The original set is returned without pruning when it already resolves the
    graph. If repair is necessary, the repaired set is pruned once and then
    checked exactly; an unsafe probabilistic pruning result is discarded.
    """

    if g.is_directed():
        raise ValueError("global collision repair requires an undirected graph")

    node_count = g.vcount()
    if node_count == 0:
        raise ValueError("global collision repair requires at least one vertex")
    original_set = (
        resolving_set if isinstance(resolving_set, set) else set(resolving_set)
    )
    invalid_landmarks = sorted(
        (
            landmark
            for landmark in original_set
            if not isinstance(landmark, Integral)
            or landmark < 0
            or landmark >= node_count
        ),
        key=repr,
    )
    if invalid_landmarks:
        raise ValueError(
            f"resolving_set contains invalid vertex IDs: {invalid_landmarks}"
        )

    distances = _normalized_distance_matrix(g, dist_matrix)
    signature_classes = _global_signature_classes(
        node_count,
        original_set,
        distances,
    )
    collision_pairs_before = count_colliding_pairs(signature_classes)

    if _is_resolving_by_project_convention(
        node_count,
        original_set,
        collision_pairs_before,
    ):
        return GlobalRepairRun(
            resolving_set=original_set,
            original_size=len(original_set),
            repaired_pre_prune_size=len(original_set),
            repair_probes=(),
            collision_pairs_before=collision_pairs_before,
            collision_pairs_after=collision_pairs_before,
            pruned_after_repair=0,
        )

    nodes = tuple(range(node_count))
    repaired_set = set(original_set)
    candidates = set(nodes) - repaired_set
    repair_probes = []
    current_collision_pairs = collision_pairs_before

    # A singleton is the one project-convention exception to strict collision
    # reduction: it needs landmark 0 even though its pair count starts at zero.
    if node_count == 1 and not repaired_set:
        repaired_set.add(0)
        candidates.remove(0)
        repair_probes.append(0)
        signature_classes = extend_signatures(
            nodes,
            0,
            signature_classes,
            distances,
        )

    while current_collision_pairs > 0:
        if not candidates:
            raise RuntimeError(
                "global collision repair exhausted all landmark candidates"
            )

        scored_candidates = [
            (
                collision_score_of_landmark_candidate(
                    nodes,
                    candidate,
                    signature_classes,
                    distances,
                ),
                candidate,
            )
            for candidate in sorted(candidates)
        ]
        next_collision_pairs, best_candidate = min(scored_candidates)
        if next_collision_pairs >= current_collision_pairs:
            raise AssertionError(
                "a global repair probe must strictly reduce colliding pairs"
            )

        signature_classes = extend_signatures(
            nodes,
            best_candidate,
            signature_classes,
            distances,
        )
        repaired_set.add(best_candidate)
        candidates.remove(best_candidate)
        repair_probes.append(best_candidate)
        current_collision_pairs = next_collision_pairs

    repaired_pre_prune_size = len(repaired_set)
    pruned_set = prune_resolving_set_zobrist_fast(
        g,
        repaired_set,
        distances,
    )
    collision_pairs_after_pruning = _exact_collision_pairs(
        node_count,
        pruned_set,
        distances,
    )

    if not _is_resolving_by_project_convention(
        node_count,
        pruned_set,
        collision_pairs_after_pruning,
    ):
        final_set = repaired_set
        collision_pairs_after = _exact_collision_pairs(
            node_count,
            final_set,
            distances,
        )
    else:
        final_set = pruned_set
        collision_pairs_after = collision_pairs_after_pruning

    if not _is_resolving_by_project_convention(
        node_count,
        final_set,
        collision_pairs_after,
    ):
        raise RuntimeError("global collision repair produced an invalid set")

    return GlobalRepairRun(
        resolving_set=final_set,
        original_size=len(original_set),
        repaired_pre_prune_size=repaired_pre_prune_size,
        repair_probes=tuple(repair_probes),
        collision_pairs_before=collision_pairs_before,
        collision_pairs_after=collision_pairs_after,
        pruned_after_repair=repaired_pre_prune_size - len(final_set),
    )
