import random
import unittest

import igraph as ig
import networkx as nx

from algorithms.reverse_elimination import reverse_eliminate
from functions.resolving_functions import checkIfResolvingSet_igraph


class ReverseEliminationTests(unittest.TestCase):
    def test_matches_exact_deletion_including_disconnected_graphs(self):
        graphs = [ig.Graph.Ring(12), ig.Graph.Full(10), ig.Graph(n=10), ig.Graph(n=1)]
        graphs += [
            ig.Graph.from_networkx(nx.random_geometric_graph(35, radius, seed=19))
            for radius in (0.03, 0.2, 0.5, 1.4)
        ]
        for graph in graphs:
            distances = graph.distances()
            for seed in range(4):
                order = list(range(graph.vcount()))
                random.Random(seed).shuffle(order)
                expected = set(order)
                for landmark in order:
                    candidate = expected - {landmark}
                    if checkIfResolvingSet_igraph(graph, candidate, distances):
                        expected = candidate
                run = reverse_eliminate(graph, distances, seed=seed, order=order)
                self.assertEqual(run.resolving_set, expected)
                for landmark in run.resolving_set:
                    self.assertFalse(checkIfResolvingSet_igraph(
                        graph, run.resolving_set - {landmark}, distances
                    ))

    def test_complete_and_empty_edge_graphs_need_n_minus_one(self):
        for graph in (ig.Graph.Full(15), ig.Graph(n=15)):
            self.assertEqual(len(reverse_eliminate(graph).resolving_set), 14)

    def test_seed_is_reproducible_without_changing_global_random_state(self):
        graph = ig.Graph.Ring(15)
        before = random.getstate()
        self.assertEqual(reverse_eliminate(graph, seed=21), reverse_eliminate(graph, seed=21))
        self.assertEqual(random.getstate(), before)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            reverse_eliminate(ig.Graph(n=0))
        with self.assertRaises(ValueError):
            reverse_eliminate(ig.Graph(n=3), order=[0, 0, 1])
        with self.assertRaises(ValueError):
            reverse_eliminate(ig.Graph(n=3, directed=True))


if __name__ == "__main__":
    unittest.main()
