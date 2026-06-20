import time
import networkx as nx
import igraph as ig
import pandas as pd

from algorithms.grid_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_grid
)

from algorithms.circle_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_circle
)

from algorithms.zoomed_square_method import (
    get_metric_dimension_of_graph_with_pruning_igraph_zoomed_square
)

from algorithms.ich_multilateration import (
    get_metric_dimension_of_graph_ich
)

from functions.resolving_functions import (
    checkIfResolvingSet_igraph
)

###################################################
# Parameters
###################################################

n_values = [10, 50, 100, 200, 500, 1000]
r_values = [0.1, 0.3, 0.5, 0.7, 0.9]

results = []

###################################################
# Benchmark
###################################################

for n in n_values:
    for r in r_values:

        print(f"\nn = {n}, r = {r}")

        # Generate one graph
        G_nx = nx.random_geometric_graph(n, r)
        G_ig = ig.Graph.from_networkx(G_nx)

        dist_matrix = G_ig.distances()

        #########################################
        # Grid method
        #########################################

        start = time.time()

        rs_grid = (
            get_metric_dimension_of_graph_with_pruning_igraph_grid(
                G_nx,
                r
            )
        )

        grid_time = time.time() - start

        #########################################
        # Circle method
        #########################################

        start = time.time()

        rs_circle = (
            get_metric_dimension_of_graph_with_pruning_igraph_circle(
                G_nx,
                r
            )
        )

        circle_time = time.time() - start

        #########################################
        # Zoomed square method
        #########################################

        start = time.time()

        rs_square = (
            get_metric_dimension_of_graph_with_pruning_igraph_zoomed_square(
                G_nx,
                r
            )
        )

        square_time = time.time() - start

        #########################################
        # ICH
        #########################################

        start = time.time()

        rs_ich = (
            get_metric_dimension_of_graph_ich(
                G_nx
            )
        )

        ich_time = time.time() - start

        #########################################
        # Check correctness
        #########################################

        grid_valid = checkIfResolvingSet_igraph(
            G_ig,
            rs_grid,
            dist_matrix
        )

        circle_valid = checkIfResolvingSet_igraph(
            G_ig,
            rs_circle,
            dist_matrix
        )

        square_valid = checkIfResolvingSet_igraph(
            G_ig,
            rs_square,
            dist_matrix
        )

        ich_valid = checkIfResolvingSet_igraph(
            G_ig,
            rs_ich,
            dist_matrix
        )

        #########################################
        # Save results
        #########################################

        results.append({

            "n": n,
            "r": r,

            "grid_size": len(rs_grid),
            "grid_time": grid_time,
            "grid_valid": grid_valid,

            "circle_size": len(rs_circle),
            "circle_time": circle_time,
            "circle_valid": circle_valid,

            "square_size": len(rs_square),
            "square_time": square_time,
            "square_valid": square_valid,

            "ich_size": len(rs_ich),
            "ich_time": ich_time,
            "ich_valid": ich_valid

        })

###################################################
# Save to Excel
###################################################

df = pd.DataFrame(results)

df.to_excel(
    "metric_dimension_results.xlsx",
    index=False
)

print("\nBenchmark complete.")