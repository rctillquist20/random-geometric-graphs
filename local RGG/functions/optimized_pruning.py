"""Shared optimized deletion kernel for full or partial landmark sets."""

from numbers import Integral
import random

from functions.resolving_functions import checkIfResolvingSet_igraph


def prune_resolving_set_optimized(graph, landmarks, distances, seed=0, order=None, bits=128):
    """Prune a supplied set with cached fingerprints and one deletion scan.

    Both forward and reverse experiments call this exact function. The only
    difference is their initial set. Invalid starting sets are returned
    unchanged so the existing global repair stage can resolve them. A hash
    collision can reject a safe deletion but cannot accept an unsafe one.
    Nonempty final outputs are checked exactly after pruning.
    """
    n = graph.vcount()
    initial = set(landmarks)
    if graph.is_directed():
        raise ValueError("optimized pruning requires an undirected graph")
    if any(not isinstance(node, Integral) or not 0 <= node < n for node in initial):
        raise ValueError("landmarks must be valid vertex indices")
    if bits < 64:
        raise ValueError("use at least 64 fingerprint bits")
    if not initial:
        return set()
    if len(distances) != n or any(len(row) != n for row in distances):
        raise ValueError("distance matrix must be n by n")

    rng = random.Random(seed)
    deletion_order = sorted(initial) if order is None else list(order)
    if len(deletion_order) != len(initial) or set(deletion_order) != initial:
        raise ValueError("order must be a permutation of the initial landmarks")
    if order is None:
        rng.shuffle(deletion_order)

    hashes = [0] * n
    contributions = {}
    for landmark in sorted(initial):
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
        contributions[landmark] = contribution

    # Removing coordinates cannot resolve a collision in an invalid input.
    if len(set(hashes)) != n:
        return initial
    remaining = set(initial)
    for landmark in deletion_order:
        if len(remaining) == 1:
            break
        adjusted = [value ^ code for value, code in zip(hashes, contributions[landmark])]
        if len(set(adjusted)) == n:
            remaining.remove(landmark)
            hashes = adjusted
    if not checkIfResolvingSet_igraph(graph, remaining, distances):
        raise RuntimeError("shared optimized pruning failed exact validation")
    return remaining
