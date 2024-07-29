import matplotlib.pyplot as plt
import multilateration as geo
# import shelf.improved_ich as im
# import shelf.geopigeon as pigeon
import networkx as nx
import random
# import os

## MAIN LAB FILES ##
# import decode
import analysis
import geohat


def get_items_of_first_key(dictionary):
    first_key = next(iter(dictionary))
    return dictionary[first_key]

# Check set values is in list?
def any_set_element_in_list(set_, list_):
  return any(item in list_ for item in set_)



nodes = 34
radius = 0.2

seed_list = [437162]
# seed_list = [267652,
#              439468,
#              657341,
#              289604,
#              852397,
#              437162,
#              726260,
#              614008,
#              763785,
#              628768]

# Test for same # of components and same # edges.
# Return out of 10 similar graphs the pick rate frequency for close to unique
# columns.


def get_frequency(seed_list):
    frequency = 0
    for seed in seed_list:
        G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
        matrix = analysis.get_distance_matrix(
            G, submatrix=False, display=False)
        items = get_items_of_first_key(
            geohat.get_close_to_unique_columns(matrix=matrix))
        analysis.get_unique_resolve_runs(filename=f'{seed}_{radius}',
                                                       nodes=nodes, radius=radius, relative_path='metric_d/close_pick/',
                                                       seed=seed, G=G)
        resolve_set = analysis.get_unique_numbers(f'metric_d/close_pick/{seed}_{radius}.txt')
        if any_set_element_in_list(resolve_set, items):
            frequency += 1
    return frequency


# Increase Radius, more Edges.
# Same Fixed positions.
# k-1 isolated vertices pick matter?
# Harder for Graph patterns. Harder when small.


def get_graphs_seeds(nodes, radius, edges, components, max_seeds_count):
    seed_list = []
    for seed in range(1, 1000000):
        # seed = random.randint(1, 1000000)
        G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
        # (G.number_of_edges() == edges) and 
        if (components == nx.number_connected_components(G)):
            seed_list.append(seed)
        if len(seed_list) == max_seeds_count:
            break
    return seed_list


# print(get_frequency(seed_list))
#print(get_graphs_seeds(nodes = 34, radius = 0.2, edges = 34, components = 5, max_seeds_count = 1))

# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=5)

# print(nx.number_connected_components(G))


# nx.draw(G, with_labels=True, font_weight='bold',
#                     node_color='cyan', edge_color='black')
# plt.show()
