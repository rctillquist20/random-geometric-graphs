# import matplotlib.pyplot as plt
# import networkx as nx
# from analysis import draw_graph 
import decode
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

def draw_graph(G, static_pos=None, show_resolving=True, r_set=[]):
    try:
        if show_resolving == True:
            color_map = []
            for node in G:
                if node in r_set:
                    color_map.append('red')
                else:
                    color_map.append('cyan')
            nx.draw(G, pos=static_pos, with_labels=True, font_weight='bold',
                    node_color=color_map, edge_color='black')
        else:
            nx.draw(G, with_labels=True, font_weight='bold',
                    node_color='cyan', edge_color='black')
        plt.show()
    except:
        print('Error: Specific graph cannot be drawn.')



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

nodes = 92
radius = 0.12999999999999998
seed = 267868

G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
get_distance_matrix(G)
# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

