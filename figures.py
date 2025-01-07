#####
# Draws the Graphs for Metric and Time by ascending in Total Edges Size
#####

import time
import decode
import analysis
import matplotlib.pyplot as plt
import numpy as np
import multilateration as geo
import networkx as nx
import os
import geohat
import sys
# sys.path.append('/Users/evanalba/random-geometric-graphs/shelf')
# import degnite

nodes = 34
radius = 0.2
# seed = 726260
# seed_list = [852397, 763785, 726260, 657341,
#              628768, 614008, 439468, 437162, 289604, 267652]

# EDGES ASCENDING!!
seed_list = [267652,
             439468,
             657341,
             289604,
             852397,
             437162,
             726260,
             614008,
             763785,
             628768]

geo_r_set = []
ich_r_set = []
geo_runtime = []
ich_runtime = []
# # 34.txt --> 628768


repeat = 1
# seed_list = [763785]

metric_count = []
false_count = []
metric_time = []
for seed in seed_list:
    G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
    matrix = analysis.get_distance_matrix(G, submatrix=False, display=False)
    for _ in range(repeat):
        geo_r, geo_execution_time = degnite.get_stats_degnite(G, matrix)
        if geo_r == False:
            metric_count.append(-1)
        else:
            metric_count.append(len(geo_r))
        metric_time.append(geo_execution_time)
        print('Metric Count:\n', metric_count, '\n')
        print('Metric Time:\n', metric_time, '\n')

        # print(geo_r_set)
        # print(f'\nGEO RUNTIME:\n{geo_runtime}')
        # start = time.perf_counter()
        # resSet = geo.ich(G)
        # end = time.perf_counter()
        # execution_time = (end - start)
        # metric_count.append(len(resSet))
        if geo_r == False:
            false_count.append(1)
        else:
            false_count.append(0)
        # metric_time.append(execution_time)

### STATE YOUR METHOD ###
method = 'ICH vs Random'

### ICH METRIC DIMENSION ###

x_axis_data = ('(267652 | 50)', '(657341 | 52)', '(439468 | 52)',
               '(852397 | 54)', '(289604 | 54)', '(437162 | 56)',
               '(726260 | 57)', '(614008 | 60)', '(763785 | 65)',
               '(628768 | 84)')

# Note: 0 == False
bar_groups = {'Metric Dimension': metric_count,
              'False': false_count}

x = np.arange(len(x_axis_data))
width = 0.25
multiplier = 0

fig, ax = plt.subplots()

for attribute, measurement in bar_groups.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel('Metric Dimension')
ax.set_xlabel('Seed : # of Edges ')
ax.set_title(method + ' Metric Dimension (Nodes: 34, Radius: 0.2)')
ax.set_xticks(x + width/2, x_axis_data)
ax.legend(loc='upper right', ncols=2)
ax.set_ylim(0, 250)

plt.show()

#######

### ICH TIME ###

x_axis_data = ('(267652 | 50)', '(657341 | 52)', '(439468 | 52)',
               '(852397 | 54)', '(289604 | 54)', '(437162 | 56)',
               '(726260 | 57)', '(614008 | 60)', '(763785 | 65)',
               '(628768 | 84)')

bar_groups = {'Time (Seconds)': metric_time}

x = np.arange(len(x_axis_data))
width = 0.25
multiplier = 0

fig, ax = plt.subplots()

for attribute, measurement in bar_groups.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Note: Look at pattern with bar_groups for making some general y-axis label!
ax.set_ylabel('Time (Seconds)')
ax.set_xlabel('Seed : # of Edges ')
ax.set_title(method + ' Time (Nodes: 34, Radius: 0.2)')
ax.set_xticks(x, x_axis_data)
ax.legend(loc='upper right', ncols=1)

plt.show()

####

# plt.hist(data, density=True)
# Freq = True
# Count = False

####


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
# nodes = 32
# radius = 0.2
# seed = 437162
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# filename = f"metric_d/d_10/34/{seed}.txt"
# r = analysis.get_unique_numbers(filename)
# print(r)
# analysis.draw_graph(G, r_set=r, seed=seed)
