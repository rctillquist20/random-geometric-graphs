import decode
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

# Returns us a drawn graph that can be show the resolving set
# in order to find the metric dimension.


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

# Returns us a displayed distance matrix in order to find the metric
# dimension based on unique different ordered vectors.


def get_distance_matrix(G):

    distances = dict(nx.all_pairs_shortest_path_length(G))
    # print(distances)

    distance_matrix = [[0 for _ in range(len(G.nodes()))]
                       for _ in range(len(G.nodes()))]

    for i, node_i in enumerate(G.nodes()):
        for j, node_j in enumerate(G.nodes()):
            if node_i != node_j:
                distance_matrix[i][j] = distances.get(node_i, {}).get(node_j, float('inf'))

            else:
                distance_matrix[i][j] = 0

    print("Shortest Distance Matrix:\n")
    for row in distance_matrix:
        print(row)

# Trying to find unique Resolving Sets for a given graph using the brute force
# method.
#
# get_brute_force_runs(15, nodes=nodes, radius=radius, seed=seed, G=G)


def get_unique_resolve_runs(filename, nodes, radius, seed, G, repeat=100):
    # if not os.path.exists(f'metric_d/d_10/{filename}.txt'):
        with open(f'metric_d/d_10/{filename}.txt', 'w') as f:
            f.write(f'Nodes: {nodes}, Radius: {radius}, Seed: {seed}, Edges: {nx.number_of_edges(G)}\n\n')
            f.close()
   
        # Get Resolve Set and check if it in file, if not, append.
        for _ in range(repeat):
            resolve_set = str(geo.bruteForce(G))
            resolve_set_in_file = False
            with open(f'metric_d/d_10/{filename}.txt', 'r') as f:
                for line in f:
                    if resolve_set in line:
                        resolve_set_in_file = True
                f.close()
            if resolve_set_in_file == False:
                with open(f'metric_d/d_10/{filename}.txt', 'a') as f:
                    f.write(f'{resolve_set}\n\n')
                    f.close()


# Modify the values here as need to analyze deeply a specific graph.
nodes = 15
radius = 0.30000000000000004
seed = 161285
# analysis/graph_15_0.30000000000000004_161285.png

G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

# Graph Position Access Snippet!
# for node, pos in G.nodes(data='pos'):
#     print(pos)

# Example of collected Static Position drawn on graph.
# Note: Have one parameter of output=False so you so do not get double output
# from decode.get_data()
#
# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=True)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

# Example of collected Random Position drawn on graph.
# draw_graph(G, r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed)[3])

# print('Edges: ', nx.number_of_edges(G))

get_distance_matrix(G)
# get_unique_resolve_runs(nodes, nodes=nodes, radius=radius, seed=seed, G=G)
# print(geo.bruteForce(G))


# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])
