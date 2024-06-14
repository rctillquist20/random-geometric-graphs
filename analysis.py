# import decode
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx

nodes = 5
radius = 1
seed = 123

# TODO: Make it where the resolving set can show based on a color
# in the MatPlotLib Graph
def draw_graph(G, show_resolving=True):
    nx.draw(G, with_labels=True, font_weight='bold',
            node_color='cyan', edge_color='black')
    plt.show()


def get_distance_matrix(G):

    distances = dict(nx.all_pairs_shortest_path_length(G))

    distance_matrix = [[0 for _ in range(len(G.nodes()))]
                       for _ in range(len(G.nodes()))]

    for i, node_i in enumerate(G.nodes()):
        for j, node_j in enumerate(G.nodes()):
            if node_i != node_j:
                distance_matrix[i][j] = distances[node_i][node_j]

            else:
                distance_matrix[i][j] = 0

    print("Shortest Distance Matrix:")
    for row in distance_matrix:
        print(row)


G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
draw_graph(G)
