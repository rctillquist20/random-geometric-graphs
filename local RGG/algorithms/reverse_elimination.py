"""Reverse deletion from the full vertex set, with exact final validation."""

from dataclasses import dataclass
import random

from functions.resolving_functions import checkIfResolvingSet_igraph


@dataclass(frozen=True)
class ReverseEliminationRun:
    resolving_set: set[int]
    deletion_order: tuple[int, ...]
    deleted: tuple[int, ...]


def reverse_eliminate(g, dist_matrix=None, seed=0, order=None, bits=128):
    """Try deleting each landmark once from an initially complete set.

    A failed deletion never becomes possible after more landmarks are removed,
    so restarting the scan is unnecessary. Random fingerprints accelerate the
    same test as the project's Zobrist pruning. Equal distance signatures always
    have equal hashes: hash collisions can only reject a safe deletion, never
    accept an unsafe one. The final set is additionally checked exactly.

    IDs are igraph vertex indices. Infinity denotes unreachable vertices,
    following the project's convention for disconnected graphs. Order is a
    seeded random permutation unless an explicit permutation is supplied.
    """
    n = g.vcount()
    if g.is_directed() or n == 0:
        raise ValueError("requires a nonempty undirected graph")
    if bits < 64:
        raise ValueError("use at least 64 fingerprint bits")
    distances = g.distances() if dist_matrix is None else dist_matrix
    if len(distances) != n or any(len(row) != n for row in distances):
        raise ValueError("distance matrix must be n by n")
    rng = random.Random(seed)
    deletion_order = list(range(n)) if order is None else list(order)
    if len(deletion_order) != n or set(deletion_order) != set(range(n)):
        raise ValueError("order must be a permutation of all vertex indices")
    if order is None:
        rng.shuffle(deletion_order)

    # Store each landmark's contribution to every vertex's fingerprint.
    contributions = []
    hashes = [0] * n
    for landmark in range(n):
        codes = {}
        contribution = []
        for vertex in range(n):
            distance = distances[landmark][vertex]
            if distance < 0:
                distance = float("inf")
            if distance not in codes:
                codes[distance] = rng.getrandbits(bits)
            value = codes[distance]
            contribution.append(value)
            hashes[vertex] ^= value
        contributions.append(contribution)

    remaining = set(range(n))
    deleted = []
    for landmark in deletion_order:
        if len(remaining) == 1:
            break  # the project's checker requires a nonempty set
        adjusted = [
            fingerprint ^ contribution
            for fingerprint, contribution in zip(hashes, contributions[landmark])
        ]
        if len(set(adjusted)) == n:
            remaining.remove(landmark)
            deleted.append(landmark)
            hashes = adjusted

    if not checkIfResolvingSet_igraph(g, remaining, distances):
        raise RuntimeError("reverse elimination failed exact validity check")
    return ReverseEliminationRun(remaining, tuple(deletion_order), tuple(deleted))
