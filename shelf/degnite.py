import networkx as nx
import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
import analysis
from geohat import is_resolving_set

# G = nx.Graph()
# G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F'])
# G.add_edges_from([('A', 'B'), ('A', 'D'), ('D', 'B'), ('B', 'E'), ('B', 'C'), ('C', 'F')])

# # Calculate all-pairs shortest paths
# distances = dict(nx.all_pairs_shortest_path_length(G))

# # Create the empty distance matrix
# distance_matrix = [[0 for _ in range(len(G.nodes()))] for _ in range(len(G.nodes()))]

# # Fill the distance matrix with shortest path lengths
# for i, node_i in enumerate(G.nodes()):
#   for j, node_j in enumerate(G.nodes()):
#     if node_i != node_j:
#       distance_matrix[i][j] = distances[node_i][node_j]
#     # Set diagonal elements to 0 (distance to itself)
#     else:
#       distance_matrix[i][j] = 0


# 1. node's degree + # of inifinites for that node(Represented as -1)
# 1st Option = HIGHEST score based on equation descending.
# 2nd Option = LOWEST score based on equation ascending.
# Note: IF TIE --> Pick by original ordering G node labeling from 0 to #.
def degnite(G, matrix):
    score = {}
    for i in range(G.number_of_nodes()):
    #    print(G.degree['A'])
       score[i] = G.degree(i) + matrix[i].count(-1)
       
    # print(score)
    # print('\n')
    # print(distance_matrix)
    # print(score)
    # print('\n')
    final_score = sorted(score.items(), key=lambda x: x[1])
    r_set = []
    for i in range(G.number_of_nodes()):
        r_set.append(final_score[i][0])
        is_r = is_resolving_set(distance_matrix=matrix, test_set = r_set)
        if is_r == True:
            return r_set
        # print(r_set, '\n')

    # print(sorted(score.items(), key=lambda x: x[1]))
    # print(test)
    return False


# 2. (node's degree + # of inifinite reachability) // # of components
def degnitejr(G, matrix):
    score = {}
    for i in range(G.number_of_nodes()):
    #    print(G.degree['A'])
       score[i] = (G.degree(i) + matrix[i].count(-1)) // nx.number_connected_components(G)
       
    # print(score)
    # print('\n')
    # print(distance_matrix)
    # print(score)
    # print('\n')
    final_score = sorted(score.items(), key=lambda x: x[1])
    r_set = []
    for i in range(G.number_of_nodes()):
        r_set.append(final_score[i][0])
        is_r = is_resolving_set(distance_matrix=matrix, test_set = r_set)
        if is_r == True:
            return r_set
        # print(r_set, '\n')

    # print(sorted(score.items(), key=lambda x: x[1]))
    # print(test)
    return False

import time
def get_stats_degnite(G, matrix):
    start = time.perf_counter()
    r_set = degnitejr(G, matrix)
    end = time.perf_counter()
    execution_time = (end - start)
    return r_set, execution_time

# nodes = 34
# radius = 0.2
# seed_list = [267652, 289604, 437162, 439468,
#              614008, 628768, 657341, 726260, 763785, 852397]
# # seed = 267652
# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     matrix = analysis.get_distance_matrix(G=G)
#     # degnite(G=G, matrix=matrix)
#     get_stats_degnite(G, matrix)

# print(degnite(G=G, matrix=matrix))
# list(set(arr1) - set(arr2))
