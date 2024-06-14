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

print('\nICH Algorithm:')
print(geo.ich(G))
print('\nBrute Force:\n')
print(geo.bruteForce(G))

nx.draw(G, with_labels=True, font_weight='bold', node_color='red', edge_color='black')
plt.show()
