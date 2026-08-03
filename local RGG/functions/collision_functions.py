"""Helpers for selecting landmarks by the number of unresolved node pairs."""

from collections import Counter
from collections.abc import Hashable, Iterable, Mapping


def distance_code(distance):
    """Return a stable, hashable code for a finite or infinite graph distance."""
    return int(distance) if distance < float("inf") else -1


def count_colliding_pairs(signature_classes: Mapping[int, Hashable]) -> int:
    """Count unordered node pairs that belong to the same signature class."""
    signature_counts = Counter(signature_classes.values())
    return sum(count * (count - 1) // 2 for count in signature_counts.values())


def collision_score_of_landmark_candidate(
    nodes: Iterable[int],
    candidate: int,
    current_signature_classes: Mapping[int, Hashable],
    dist_matrix,
) -> int:
    """Count the node-pair collisions left after adding ``candidate``.

    ``current_signature_classes`` assigns equal labels to nodes with equal
    signatures under the landmarks already chosen in the neighborhood. The
    candidate's distance refines those classes. Lower scores are better; zero
    resolves all pairs.
    """
    signature_counts = Counter(
        (
            current_signature_classes.get(node, 0),
            distance_code(dist_matrix[node][candidate]),
        )
        for node in nodes
    )
    return sum(count * (count - 1) // 2 for count in signature_counts.values())


def extend_signatures(
    nodes: Iterable[int],
    candidate: int,
    current_signature_classes: Mapping[int, Hashable],
    dist_matrix,
) -> dict[int, int]:
    """Refine compact signature-class labels using ``candidate`` distances.

    Class labels preserve exactly the equality relation between full distance
    signatures without storing and repeatedly hashing ever-growing tuples.
    """
    class_ids = {}
    updated_classes = {}
    for node in nodes:
        refined_key = (
            current_signature_classes.get(node, 0),
            distance_code(dist_matrix[node][candidate]),
        )
        if refined_key not in class_ids:
            class_ids[refined_key] = len(class_ids)
        updated_classes[node] = class_ids[refined_key]
    return updated_classes


def select_collision_minimizing_candidate(
    nodes: Iterable[int],
    candidates: Iterable[int],
    current_signature_classes: Mapping[int, Hashable],
    dist_matrix,
) -> int:
    """Select the candidate leaving the fewest colliding node pairs.

    Candidate iteration order is preserved as the tie-breaker. Probe-guided
    callers should therefore pass candidates nearest to the probe first.
    """
    nodes = tuple(nodes)
    candidates = tuple(candidates)
    if not candidates:
        raise ValueError("at least one landmark candidate is required")

    return min(
        candidates,
        key=lambda candidate: collision_score_of_landmark_candidate(
            nodes,
            candidate,
            current_signature_classes,
            dist_matrix,
        ),
    )
