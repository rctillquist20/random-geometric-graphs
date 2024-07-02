#This is what I have so far, not sure how effective it is.
import networkx as nx
import numpy as np
from itertools import combinations

def find_minimum_cuts(G):
    return nx.algorithms.connectivity.stoer_wagner(G)

def form_clusters(G, min_cuts):
    """
    Form clusters in the graph based on the minimum cuts.
    """
    clusters = []
    while cut_value < threshold in min_cuts:
        clusters.append(list(partition))
        #do a recursive cut
        #cut a graph, then recursively call on func to cut more as needed
        #stop when all cuts are bigger than threshold
        #store in list
        #run ICH algo on each component seperately
        #subgraph generates new graph w new nodes & edges between nodes
        #this is called an "induced subgraph"
        #cut_value is number of edges to be removed
        #smaller threshold the better, about 3-5

    return clusters
