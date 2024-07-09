import decode
import analysis
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os
import geohat

# Find the unique R
# nodes = 34
# radius = 0.2
# # seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]
# seed_list = [437162]

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)

# create a dictionary with keys and values
# from collections import defaultdict

# countries = {1: [3, 4], [[0,1], [9, 10]], 22: 9, 5: 3}
# Dictionary Format:
# { Count of Occurence : [ [ column], [ [Column(s) of Element], [Column(s) of Element] ] }
# countries = {1: [[8], [1]], 2: [[1, 2], [0], [0, 1]], 3: [[0], [1, 2, 3]], 4: [[-1], [2, 3]]}

# Add Element
# countries[1][0].append(9)
# Add Column List Item
# countries[1][1][0].append(7)
# Add Column List
# countries[1][1].append([])
# print(countries)
# Add Key
# countries[2] = [[], [[]]]
# print(countries)

# countries[5] = 69
# for index, item in enumerate(countries):
#     print(index)
# i = 0
# for key, item in countries.items():
#     print(i)
#     i += 1
# my_list = {1: [[8], [1]], 2: [[1, 2], [0], [0, 1]], 3: [[0], [1, 2, 3]], 4: [[-1], [2, 3]]}

# for key, value in my_list.items():
#   # value[0] <-- First List of Elements
#   for inner_list in value[1:]:
#     for column in inner_list:
#       print(f"Key: {key}, Column: {column}")
# def iterate_increasing_slice(data_list, start_index=0):
#     slice_size = 1
#     while slice_size <= len(data_list):
#         yield data_list[start_index: slice_size]
#         slice_size += 1

# # Example usage
# data_list = [1, 2, 3, 4, 5, 6]

# for slice in iterate_increasing_slice(data_list):
#     print(slice)

# import matplotlib.pyplot as plt

# # Define your data
# fruits = ["Apples", "Oranges", "Bananas", "Mangoes"]
# sales = [1000, 850, 1500, 1200]  # Sales of each fruit

# # Create the bar chart
# plt.bar(fruits, sales)

# # Add labels and title
# plt.xlabel("Difference (ICH - Geohat)")
# # Frequency???? Meaning??
# plt.ylabel("Frequency")
# plt.title("Resolving Set Size Differences")

# plt.show()

import time

nodes = 34
radius = 0.2
# seed = 726260
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]
geo_r_set = []
ich_r_set = []
geo_runtime = []
ich_runtime = []
# # 34.txt --> 628768


# repeat = 1
# seed_list = [763785]

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     matrix = analysis.get_distance_matrix(G, submatrix=False, display=False)
#     for _ in range(repeat):
#         geo_r, geo_execution_time = geohat.get_stats_geohat(matrix, repeat=1, option=[1,2,3])
#         geo_r_set.append(geo_r)
#         geo_runtime.append(geo_execution_time)
#         print(geo_r_set)
#         print(f'\nGEO RUNTIME:\n{geo_runtime}')
#         start = time.perf_counter()
#         resSet = geo.ich(G)
#         end = time.perf_counter()
#         execution_time = (end - start)

# plt.hist(data, density=True)
# Freq = True
# Count = False



# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# resolve_set = geo.bruteForce(G)
# resSet = geo.ich(G)
# print(resolve_set)

# nodes = 34
# radius = 0.2
# seed = 437162
# r_set=[1, 18, 19, 21, 24, 27, 30]

# decode.get_data(nodes=nodes, radius=radius, seed=seed)
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# test = analysis.get_distance_matrix(G, submatrix=True, r_set=r_set)
# for x in test:
#     print(x, '\n')
# print(geohat.is_resolving_set(analysis.get_distance_matrix(G, r_set=r_set), test_set=r_set))

# analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)


# nodes = 32
# radius = 0.2
# seed = 852397
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

# draw_graph(G, static_pos=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False))




# # Example Usage
# 65, 61, 439, 20s
            # data_num = 10
            # os.makedirs(f'images/d_{data_num}/figures', exist_ok=True)
            # plt.savefig(
            #     f"images/d_{data_num}/figures/{seed}.png")
# def get_graph
# seed_list = [852397, 763785, 726260, 628768, 437162]
# for seed in seed_list:
#     nodes = 32
#     radius = 0.2
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     filename = f"metric_d/d_10/34/{seed}.txt"
#     analysis.draw_graph(G, r_set=analysis.get_unique_numbers(filename), seed=seed)
    # images/d_10/34/figures

#     print(f'{seed}:')
#     filename = f"metric_d/d_10/34/{seed}.txt"
#     analysis.get_unique_numbers(filename)
#     print('\n')
nodes = 32
radius = 0.2
seed = 763785
G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
filename = f"metric_d/d_10/34/{seed}.txt"
analysis.draw_graph(G, r_set=analysis.get_unique_numbers(filename), seed=seed)