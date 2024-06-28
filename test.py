import decode
import analysis
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

# Find the unique R
nodes = 34
radius = 0.2
seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]

for seed in seed_list:
    G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
    analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)


# from collections import defaultdict


# def get_least_common_elements(distance_matrix):
#     # Count occurrences of each element in the matrix
#     element_counts = defaultdict(int)
#     for row in distance_matrix:
#         for element in row:
#             element_counts[element] += 1

#     # Find the minimum count (least common)
#     print(element_counts.get(2))


# # Example usage (assuming distance_matrix is a list of lists)
# distance_matrix = [[1, 2, 2], [3, 1, 4], [2, 2, 5]]
# least_common_elements = get_least_common_elements(distance_matrix)

# print("Least common elements:", least_common_elements)
