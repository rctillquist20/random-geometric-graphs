import matplotlib.pyplot as plt
import networkx as nx


nodes = 6
radius = 0.3

G = nx.random_geometric_graph(nodes, radius)
nx.draw(G, with_labels=True, font_weight='bold', node_color='red', edge_color='black')
plt.show()

