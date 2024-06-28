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


def get_distance_matrix(G, submatrix=False, r_set=[], display=False):

    distances = dict(nx.all_pairs_shortest_path_length(G))

    distance_matrix = [[0 for _ in range(len(G.nodes()))]
                       for _ in range(len(G.nodes()))]

    for i, node_i in enumerate(G.nodes()):
        for j, node_j in enumerate(G.nodes()):
            if node_i != node_j:
                distance_matrix[i][j] = distances.get(node_i, {}).get(node_j, int('-1'))

            else:
                distance_matrix[i][j] = 0

    
    if submatrix == True: 
        node_list = list(G.nodes())
        node_indices = [node_list.index(node) for node in r_set]
        sub_matrix = [[distance_matrix[i][j] for j in node_indices] for i in node_indices]
        max_width = max(len(str(node)) for node in r_set)
        if display == True:
            print("Shortest Distance Sub Matrix:\n")
            for row in sub_matrix:
                max_width = max(max_width, len([str(val) for val in row]))
            print(' '.join([f"{node:{max_width}}" for node in r_set]), '\n')
            for row in sub_matrix:
                print(' '.join([f"{val:{max_width}}" for val in row]))
        return sub_matrix
    else:
        if display == True:
            print("Shortest Distance Matrix:\n")
            for row in distance_matrix:
                print(row)
        return distance_matrix

# Trying to find unique Resolving Sets for a given graph using the brute force
# method.
#
# get_brute_force_runs(15, nodes=nodes, radius=radius, seed=seed, G=G)


def get_unique_resolve_runs(filename, nodes, radius, seed, G, repeat=100):
    relative_path = 'metric_d/d_10/34/'
    if not os.path.exists(f'{relative_path}{filename}.txt'):
        file_type = '.txt'
        with open(f'{relative_path}{filename}{file_type}', 'w') as f:
            f.write(f'Nodes: {nodes}, Radius: {radius}, Seed: {seed}, Edges: {nx.number_of_edges(G)}\n\n')
            f.close()
   
        start_repeat_num = 1
        # Get Resolve Set and check if it in file, if not, append.
        for _ in range(repeat):
            print('REPEAT: ', start_repeat_num)
            resolve_set = str(geo.bruteForce(G))
            print('\n',resolve_set,'\n')
            resolve_set_in_file = False
            with open(f'{relative_path}{filename}{file_type}', 'r') as f:
                for line in f:
                    if resolve_set in line:
                        resolve_set_in_file = True
                f.close()
            if resolve_set_in_file == False:
                with open(f'{relative_path}{filename}{file_type}', 'a') as f:
                    f.write(f'{resolve_set}\n\n')
                    f.close()
            start_repeat_num += 1
            
    print('\nExperiments Completed!\n')


# Modify the values here as need to analyze deeply a specific graph.
# analysis/34
# analysis/34/graph_34_0.2_852397.png check
# analysis/34/graph_34_0.2_763785.png
# analysis/34/graph_34_0.2_726260.png
# analysis/34/graph_34_0.2_657341.png
# analysis/34/graph_34_0.2_628768.png
# analysis/34/graph_34_0.2_614008.png
# analysis/34/graph_34_0.2_439468.png
# analysis/34/graph_34_0.2_437162.png
# analysis/34/graph_34_0.2_289604.png
# analysis/34/graph_34_0.2_267652.png


## UNIQUE BRUTE FORCE RESOLVING TESTING ##

# nodes = 34
# radius = 0.2
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)

## DISTANCE MATRIX TESTING ##

# nodes = 92
# radius = 0.12999999999999998
# seed = 267868
# r_set=[2, 4, 6, 9, 11, 12, 18, 28]

# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# get_distance_matrix(G, submatrix=False, r_set=r_set)

## DRAW GRAPH TESTING ##
# nodes = 92
# radius = 0.12999999999999998
# seed = 267868
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

# draw_graph(G, r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed)[3])


##########################################
##### GRAPH POSITION ACCESS SNIPPET! #####
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

## EXAMPLE OF COLLECTED RANDOM POSITION DRAWN ON GRAPH ##
# draw_graph(G, r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed)[3])

# print('Edges: ', nx.number_of_edges(G))
