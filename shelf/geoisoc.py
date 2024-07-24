import time
import networkx as nx


def geoisoc(G):
    print('')

    isolated_vertices = list(nx.isolates(G))
    print(isolated_vertices)


def get_stats(nodes, matrix):
    start = time.perf_counter()
    r_set = geoisoc(nodes, matrix)
    end = time.perf_counter()
    execution_time = (end - start)
    return r_set, execution_time


nodes = 34
radius = 0.2
seed = 267652
G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

geoisoc(G)