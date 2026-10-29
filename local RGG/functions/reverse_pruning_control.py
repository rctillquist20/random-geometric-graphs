"""Reverse-elimination control using the project's existing pruning routine."""

import random

from functions.resolving_functions import checkIfResolvingSet_igraph
from functions.zobrist_functions import prune_resolving_set_zobrist_fast


def reverse_eliminate_existing_pruner(graph, distances, seed=0, bits=128):
    """Prune all vertices in the same seeded order as optimized reverse.

    Passing the permutation as a list preserves its order inside the existing
    pruning function. That function still owns its original restart-on-delete
    loop. Both controls use the same fingerprint width and an exact final check.
    """
    order = list(range(graph.vcount()))
    random.Random(seed).shuffle(order)
    previous_state = random.getstate()
    try:
        random.seed(seed)
        result = prune_resolving_set_zobrist_fast(
            graph, order, distances, bits=bits,
        )
    finally:
        random.setstate(previous_state)
    if not checkIfResolvingSet_igraph(graph, result, distances):
        raise RuntimeError("existing-pruner reverse control failed exact validation")
    return result
