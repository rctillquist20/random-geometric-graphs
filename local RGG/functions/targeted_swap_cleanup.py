"""Bounded 2-for-1 cleanup of an already valid resolving set."""

from dataclasses import dataclass
from itertools import combinations
from numbers import Integral
import random

import numpy as np

from functions.resolving_functions import checkIfResolvingSet_igraph


@dataclass(frozen=True)
class SwapCleanupRun:
    resolving_set: frozenset[int]
    pairs_checked: int
    swaps: int


def _sample_pairs(active, count, rng):
    """Sample distinct pair indices without materializing all O(k²) pairs."""
    size = len(active)
    total = size * (size - 1) // 2
    if count >= total:
        yield from combinations(active, 2)
        return
    for index in rng.sample(range(total), count):
        lo, hi = 0, size - 1
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if mid * (2 * size - mid - 1) // 2 <= index:
                lo = mid
            else:
                hi = mid
        start = lo * (2 * size - lo - 1) // 2
        yield active[lo], active[lo + 1 + index - start]


def targeted_swap_cleanup(graph, landmarks, distances, *, max_pairs=512, seed=0):
    """Try replacing two active probes with one inactive probe, up to max_pairs.

    For each sampled removal pair, group equal reduced fingerprints. An
    inactive vertex must separate every pair within each group to be useful.
    Fingerprint collisions can add spurious constraints, but they cannot hide
    a real collision. The final result is checked with exact distance tuples.
    Each accepted swap reduces the set size by one; no optimality is promised.
    """
    n = graph.vcount()
    if graph.is_directed() or n == 0:
        raise ValueError("requires a nonempty undirected graph")
    if not isinstance(max_pairs, Integral) or max_pairs < 0:
        raise ValueError("max_pairs must be a nonnegative integer")
    active = set(landmarks)
    if not active or any(not isinstance(p, Integral) or not 0 <= p < n for p in active):
        raise ValueError("landmarks must be nonempty and contain valid vertex indices")
    matrix = np.asarray(distances)
    if matrix.shape != (n, n):
        raise ValueError("distance matrix must be n by n")
    if not checkIfResolvingSet_igraph(graph, active, matrix):
        raise ValueError("cleanup requires an already resolving set")
    if len(active) < 2 or len(active) == n or max_pairs == 0:
        return SwapCleanupRun(frozenset(active), 0, 0)

    rng = random.Random(seed)

    def codes(probe):
        values, inverse = np.unique(matrix[probe], return_inverse=True)
        return np.array([rng.getrandbits(64) for _ in values], dtype=np.uint64)[inverse]

    contributions = {probe: codes(probe) for probe in sorted(active)}
    fingerprint = np.bitwise_xor.reduce(list(contributions.values()), axis=0)
    pairs_checked = swaps = 0
    while pairs_checked < max_pairs and len(active) >= 2:
        outsiders = np.array(sorted(set(range(n)) - active), dtype=np.intp)
        for a, b in _sample_pairs(sorted(active), max_pairs - pairs_checked, rng):
            pairs_checked += 1
            reduced = fingerprint ^ contributions[a] ^ contributions[b]
            order = np.argsort(reduced)
            ordered = reduced[order]
            ties = ordered[:-1] == ordered[1:]
            candidates = outsiders
            # Compare each tied vertex to every earlier vertex in its group,
            # not just its neighbor: distances like [1, 2, 1] still collide.
            group_start = 0
            for i in np.flatnonzero(ties):
                if i == 0 or not ties[i - 1]:
                    group_start = i
                for j in range(group_start, i + 1):
                    candidates = candidates[matrix[candidates, order[j]] != matrix[candidates, order[i + 1]]]
                    if not candidates.size:
                        break
                if not candidates.size:
                    break
            if not candidates.size:
                continue
            replacement = int(candidates[0])
            active.difference_update((a, b))
            active.add(replacement)
            del contributions[a], contributions[b]
            contributions[replacement] = codes(replacement)
            fingerprint = reduced ^ contributions[replacement]
            swaps += 1
            break  # Recompute candidates against the newly changed set.
        else:
            break

    if swaps and not checkIfResolvingSet_igraph(graph, active, matrix):
        raise RuntimeError("swap cleanup failed exact validation")
    return SwapCleanupRun(frozenset(active), pairs_checked, swaps)
