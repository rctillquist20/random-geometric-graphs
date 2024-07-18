import matplotlib.pyplot as plt
# import multilateration as geo
# import shelf.improved_ich as im
import shelf.geopigeon as pigeon
import networkx as nx
import os

## MAIN LAB FILES ## 
import decode
import analysis

# nodes = 92
# radius = 0.12999999999999998
# seed = 267868
# r_set=[2, 4, 6, 9, 11, 12, 18, 28]

# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# analysis.get_distance_matrix(G, submatrix=False, r_set=r_set, display=True)

# nodes = 34
# radius = 0.2
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]
# print(sorted([852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]))
# seed_list = [437162] # 4 is resolve

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     r_set = im.ich(G)
#     print(f'Resolving Set:\n{r_set}\n{len(r_set)}')
#     analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)

