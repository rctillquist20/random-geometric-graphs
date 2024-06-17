import decode
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx

# Returns us a drawn graph that can be show the resolving set
# in order to find the metric dimension.


def draw_graph(G, show_resolving=True, r_set=[]):
    if show_resolving == True:
        color_map = []
        for node in G:
            if node in r_set:
                color_map.append('red')
            else:
                color_map.append('cyan')
        nx.draw(G, with_labels=True, font_weight='bold',
                node_color=color_map, edge_color='black')
    else:
        nx.draw(G, with_labels=True, font_weight='bold',
                node_color='cyan', edge_color='black')
    plt.show()

# Returns us a displayed distance matrix in order to find the metric
# dimension based on unique different ordered vectors.


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


# Modify the values here as need to analyze deeply a specific graph.
nodes = 3
radius = 1
seed = 824506

G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)


draw_graph(G, r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed))
