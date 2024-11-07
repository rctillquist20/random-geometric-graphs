import decode
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os
import textwrap

# Returns us a drawn graph that can be show the resolving set
# in order to find the metric dimension.


def draw_graph(G, static_pos=None, show_resolving=True, r_set=[], seed=None):
    try:
        if show_resolving == True:
            color_map = []
            for node in G:
                if node in r_set:
                    color_map.append('red')
                else:
                    color_map.append('cyan')
            nx.draw(G, with_labels=True, font_weight='bold',
                    node_color=color_map, edge_color='black')
            
            # plt.savefig(f"images/d_10/10_0.4/bruteforce/{seed}.png")
        else:
            nx.draw(G, with_labels=True, font_weight='bold',
                    node_color='cyan', edge_color='black')
        plt.show()
    except:
        print('Error: Specific graph cannot be drawn.')

# Returns us a displayed distance matrix in order to find the metric
# dimension based on unique different ordered vectors.
# NOTE: Make sure to set r_set=[i for i in range(nodes)] because matrix starts 
# from 0th index. | For example, 0th index = 1st Node.
#
# Submatrix | Filters out a submatrix given some r_set. 

def get_distance_matrix(G, submatrix=False, r_set=[], display=False):

    distances = dict(nx.all_pairs_shortest_path_length(G))

    distance_matrix = [[0 for _ in range(len(G.nodes()))]
                       for _ in range(len(G.nodes()))]

    for i, node_i in enumerate(G.nodes()):
        for j, node_j in enumerate(G.nodes()):
            if node_i != node_j: 
                distance_matrix[i][j] = distances.get(
                    node_i, {}).get(node_j, -1)

            else:
                distance_matrix[i][j] = 0

    if submatrix == True:
        # node_list = list(G.nodes())
        # node_indices = [node_list.index(node) for node in r_set]
        # sub_matrix = [[distance_matrix[i][j]
        #                for j in node_indices] for i in node_indices]
        # max_width = max(len(str(node)) for node in r_set)
        sub_matrix = []
        #print(enumerate(G.nodes()))
        for row in G.nodes():
            if row in r_set:
                sub_matrix.append(distance_matrix[row])
        if display == True:
            print("Shortest Distance Sub Matrix:\n")
            for row in sub_matrix:
                print(f'{row}')
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


def get_unique_resolve_runs(filename, nodes, radius, relative_path, seed, G, repeat=1):
    file_type = '.txt'
    if not os.path.exists(f'{relative_path}{filename}{file_type}'):
        with open(f'{relative_path}{filename}{file_type}', 'w') as f:
            wrapped_header = textwrap.wrap(f'Nodes: {nodes}, Radius: {radius}, Seed: {
                                           seed}, Edges: {nx.number_of_edges(G)}', width=80)
            f.writelines(wrapped_header)
            f.close()

        k_column = 1
        start_repeat_num = 1
        for _ in range(repeat):
            print('REPEAT: ', start_repeat_num)
            resolve_set = geo.bruteForce(G, startK=k_column, numSets=-1)
            print('\n', str(resolve_set), '\n')
            resolve_set_in_file = False
            with open(f'{relative_path}{filename}{file_type}', 'r') as f:
                for line in f:
                    for i in resolve_set:
                        if str(i) in line:
                            resolve_set_in_file = True
                            break
                f.close()
            if resolve_set_in_file == False:
                with open(f'{relative_path}{filename}{file_type}', 'a') as f:
                    f.write('\n\n')
                    for i in resolve_set:
                        wrapped_element = textwrap.wrap(str(i), width=80)
                        f.writelines(wrapped_element + ['\n'])
                        k_column = len(i)
                    f.close()
            start_repeat_num += 1

    print('\nExperiments Completed!\n')


def get_r_set_difference_figures(r_set):
    print('')


def get_unique_numbers(filename):
    unique_numbers = set()
    try:
        with open(filename, 'r') as file:
            # Skip the first line
            next(file)

            for line in file:
                # Remove leading/trailing whitespace
                line = line.strip()

                # Check if line is empty (skip empty lines)
                if not line:
                    continue

                try:
                    # Assuming tuples are enclosed in parentheses
                    # Evaluate the line as a Python expression
                    numbers = eval(line)
                    # Extract individual numbers from the tuple
                    unique_numbers.update(numbers)
                except (SyntaxError, ValueError) as e:
                    print(f"Error: Line in file '{filename}' is invalid: {e}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

    if unique_numbers:
        # print("Unique numbers found:\n")
        # print(sorted(unique_numbers))
        return unique_numbers
    else:
        print("No unique numbers found in the file.")

def write_distance_matrix(filename, matrix):
    relative_path = 'metric_d/matrix'
    file_type = '.txt'
    if not os.path.exists(f'{relative_path}{filename}{file_type}'):
        with open(f'metric_d/{filename}{file_type}', 'w') as f:
            for row in matrix:
                wrapped_element = textwrap.wrap(str(row))
                f.writelines(wrapped_element + ['\n'])
        f.close()


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

# nodes = 10
# radius = 0.4000000000000001
# seed_list = [267652, 289604, 437162, 439468,
#              614008, 628768, 657341, 726260, 763785, 852397]
# seed_list = [294604, 414583, 518734, 658712, 684247, 692182, 750327, 837916, 973605, 983282]
# relative_path = 'metric_d/d_10/10_0.4/'


# for seed in seed_list:
#     print(f'\nSeed:\n{seed}\n')
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     print(get_unique_numbers(f'{relative_path}{seed}.txt'), '\n')
    
#     draw_graph(G,
#                static_pos=decode.get_data(
#                    nodes=nodes, radius=radius, seed=seed, output=False)[5],
#                r_set=get_unique_numbers(f'{relative_path}{seed}.txt'), seed=seed)
#     get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, relative_path=relative_path,seed=seed, G=G, repeat=1)

## DISTANCE MATRIX TESTING ##

# nodes = 92
# radius = 0.12999999999999998
# seed = 267652
# r_set=[2, 4, 6, 9, 11, 12, 18, 28]

# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# draw_graph(G,
#                static_pos=decode.get_data(
#                    nodes=nodes, radius=radius, seed=seed, output=False)[5],
#                r_set=get_unique_numbers(f'metric_d/d_10/34/{seed}.txt'), seed=seed)
#dm = get_distance_matrix(G, submatrix=True, r_set=get_unique_numbers(f'metric_d/d_10/34/{seed}.txt'), display=False)


# not_r = []
# for i in range(nodes):
#     if i not in get_unique_numbers(f'metric_d/d_10/34/{seed}.txt'):
#         not_r.append(i)
# dm = get_distance_matrix(G, submatrix=True, r_set=not_r, display=True)
# print(dm, '\n')
# print(not_r)
# for seed in seed_list:
# write_distance_matrix(filename='sub'+str(seed),matrix=dm)
# write_distance_matrix(filename='not'+str(seed),matrix=dm)

## DRAW GRAPH TESTING ##
# nodes = 14
# radius = 0.2637007862283646
# seed = 206860

nodes = 22
radius = 0.3788914393160148
seed = 190439
G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

file_name = 'comeback_4_1_repeat_3_to_23nodes_200graphs.list'

draw_graph(G,
           static_pos=decode.get_data(
               nodes=nodes, radius=radius, seed=seed, output=False, file_name = file_name)[5],
           r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False, file_name = file_name)[3], seed=seed, show_resolving=True)

# draw_graph(G,static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False, file_name = 'comeback_3_1_repeat_3_to_23nodes_200graphs.list')[5], r_set=[0, 2, 6])


##########################################
##### GRAPH POSITION ACCESS SNIPPET! #####
# for node, pos in G.nodes(data='pos'):
#     print(pos)

# Example of collected Static Position drawn on graph.
# Note: Have one parameter of output=False so you so do not get double output
# from decode.get_data()

# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=True)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

## EXAMPLE OF COLLECTED RANDOM POSITION DRAWN ON GRAPH ##
# draw_graph(G, r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed)[3])

# print('Edges: ', nx.number_of_edges(G))
