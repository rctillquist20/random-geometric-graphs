import importlib
import random
import unittest
from unittest.mock import patch

import igraph as ig
import networkx as nx

from algorithms.reverse_elimination import reverse_eliminate
from algorithms.shared_pruning_experimental import PRUNING_BINDINGS, shared_pruning_backend
from experiments_final_entropy_collision import _method_functions, _run_final_pipeline
from functions.optimized_pruning import prune_resolving_set_optimized
from functions.resolving_functions import checkIfResolvingSet_igraph


class SharedOptimizedPruningTests(unittest.TestCase):
    def test_full_and_partial_inputs_match_exact_seeded_deletion(self):
        graphs = [ig.Graph.Ring(14), ig.Graph.Full(12), ig.Graph(n=12), ig.Graph(n=1)]
        graphs += [ig.Graph.from_networkx(nx.random_geometric_graph(35, r, seed=13)) for r in (0.04, 0.2, 0.5)]
        for graph in graphs:
            distances = graph.distances()
            n = graph.vcount()
            for seed in range(3):
                for initial in (set(range(n)), set(range(0, n, 2)), set()):
                    order = sorted(initial)
                    random.Random(seed).shuffle(order)
                    expected = set(initial)
                    for landmark in order:
                        if checkIfResolvingSet_igraph(graph, expected - {landmark}, distances):
                            expected.remove(landmark)
                    with self.subTest(n=n, edges=graph.ecount(), initial=len(initial), seed=seed):
                        result = prune_resolving_set_optimized(graph, initial, distances, seed=seed)
                        self.assertEqual(result, expected)
                        self.assertLessEqual(result, initial)

    def test_full_set_reproduces_previous_optimized_reverse(self):
        graph = ig.Graph.from_networkx(nx.random_geometric_graph(65, 0.25, seed=91))
        distances = graph.distances()
        for seed in range(4):
            self.assertEqual(
                prune_resolving_set_optimized(graph, range(graph.vcount()), distances, seed=seed),
                reverse_eliminate(graph, distances, seed=seed).resolving_set,
            )

    def test_kernel_does_not_consume_global_random_state(self):
        graph = ig.Graph.Ring(15)
        before = random.getstate()
        prune_resolving_set_optimized(graph, range(15), graph.distances(), seed=24)
        self.assertEqual(random.getstate(), before)

    def test_wrappers_restore_every_original_binding_after_exception(self):
        original = {}
        for binding in PRUNING_BINDINGS:
            module, name = binding.rsplit(".", 1)
            original[binding] = getattr(importlib.import_module(module), name)
        with self.assertRaisesRegex(RuntimeError, "test exception"):
            with shared_pruning_backend(14):
                raise RuntimeError("test exception")
        for binding, function in original.items():
            module, name = binding.rsplit(".", 1)
            self.assertIs(getattr(importlib.import_module(module), name), function)

    def test_each_forward_family_routes_every_pruning_stage_to_shared_kernel(self):
        graph = nx.random_geometric_graph(40, 0.22, seed=18)
        converted = ig.Graph.from_networkx(graph)
        distances = converted.distances()
        methods = _method_functions(graph, 0.22, 5)
        for family in ("grid", "circle", "zoomed"):
            with self.subTest(family=family):
                with patch("algorithms.shared_pruning_experimental.prune_resolving_set_optimized", wraps=prune_resolving_set_optimized) as kernel:
                    with shared_pruning_backend(51) as stats:
                        run = _run_final_pipeline(methods[family]["collision"], 51, converted, distances, family, "collision")
                    self.assertGreaterEqual(stats.calls, 2)
                    self.assertEqual(kernel.call_count, stats.calls)
                    self.assertTrue(all(call.kwargs["bits"] == 128 and call.kwargs["seed"] == 51 for call in kernel.call_args_list))
                self.assertTrue(run["final_valid"])
                self.assertTrue(checkIfResolvingSet_igraph(converted, run["_final_set"], distances))

    def test_invalid_ids_and_duplicate_order_are_rejected(self):
        graph = ig.Graph.Ring(5)
        with self.assertRaises(ValueError):
            prune_resolving_set_optimized(graph, {5}, graph.distances())
        with self.assertRaises(ValueError):
            prune_resolving_set_optimized(graph, {0, 1}, graph.distances(), order=[0, 0])
