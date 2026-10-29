"""Scoped experimental wrappers; existing selectors and repair stay intact."""

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
import time
from unittest.mock import patch

from functions.optimized_pruning import prune_resolving_set_optimized


PRUNING_BINDINGS = (
    "algorithms.grid_collision_method.prune_resolving_set_zobrist_fast",
    "algorithms.circle_collision_method.prune_resolving_set_zobrist_fast",
    "algorithms.zoomed_square_collision_method.prune_resolving_set_zobrist_fast",
    "functions.global_collision_repair.prune_resolving_set_zobrist_fast",
    "experiments_final_entropy_collision.prune_resolving_set_zobrist_fast",
)


@dataclass
class SharedPruningStats:
    calls: int = 0
    seconds: float = 0.0


@contextmanager
def shared_pruning_backend(seed, bits=128):
    """Use one backend at every selector, repair and final pruning call.

    Used only by the sequential benchmark. Imported bindings are restored on
    exit, including exceptions. All stages use a local seeded shuffle so this
    backend does not consume the selectors' global random state.
    """
    stats = SharedPruningStats()

    def adapter(graph, landmarks, distances, **_kwargs):
        start = time.perf_counter()
        result = prune_resolving_set_optimized(
            graph, landmarks, distances, seed=seed, bits=bits,
        )
        stats.seconds += time.perf_counter() - start
        stats.calls += 1
        return result

    with ExitStack() as stack:
        for binding in PRUNING_BINDINGS:
            stack.enter_context(patch(binding, side_effect=adapter))
        yield stats
