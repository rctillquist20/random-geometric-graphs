# Playground based on Figure 1 of the Metric Dimension Paper

import matplotlib.pyplot as plt
import networkx as nx
import multilateration as geo

G = nx.Graph()
G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F'])
G.add_edges_from([('A', 'B'), ('A', 'D'), ('D', 'B'), ('B', 'E'), ('B', 'C'), ('C', 'F')])

# Calculate all-pairs shortest paths
distances = dict(nx.all_pairs_shortest_path_length(G))

# Create the empty distance matrix
distance_matrix = [[0 for _ in range(len(G.nodes()))] for _ in range(len(G.nodes()))]

# Fill the distance matrix with shortest path lengths
for i, node_i in enumerate(G.nodes()):
  for j, node_j in enumerate(G.nodes()):
    if node_i != node_j:
      distance_matrix[i][j] = distances[node_i][node_j]
    # Set diagonal elements to 0 (distance to itself)
    else:
      distance_matrix[i][j] = 0

# Print the distance matrix
print("Shortest Distance Matrix:")
for row in distance_matrix:
  print(row)

import analysis

# TODO: Fix because for some reason possible R not showing.
# ONLY [0, 2] shows when I do repeat = 100 for Brute Force???

nodes = 6
# radius = 0.2
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]

# [0, 5]
# [0, 2] 
analysis.get_unique_resolve_runs(filename='figure_1', nodes=nodes, radius=0, seed=0, G=G, repeat=100)


# print('\nICH Algorithm:')
# print(geo.ich(G))
# print('\nBrute Force:\n')
# print(geo.bruteForce(G))

# nx.draw(G, with_labels=True, font_weight='bold', node_color='red', edge_color='black')
# plt.show()
