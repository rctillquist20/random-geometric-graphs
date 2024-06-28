import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

## MAIN LAB FILES ## 
import decode
import analysis

nodes = 92
radius = 0.12999999999999998
seed = 267868
r_set=[2, 4, 6, 9, 11, 12, 18, 28]

G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
analysis.get_distance_matrix(G, submatrix=False, r_set=r_set, display=True)
