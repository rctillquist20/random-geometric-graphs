# import matplotlib.pyplot as plt
# import networkx as nx
import numpy as np
import threshold


# nodes = 6
# radius = 0.3

# G = nx.random_geometric_graph(nodes, radius)
# nx.draw(G, with_labels=True, font_weight='bold', node_color='red', edge_color='black')
# plt.show()

nList = []


rList = list(np.arange(0.02, 0.14, 0.01)) + \
    list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))


repeats = 10
for r in rList:
    # (Node, Threshold)
    if threshold.get_n_below_radius(
            starting_n=1, radius=r, repeat=repeats)[repeats-1][0] < 2000:
        nList.append(threshold.get_n_below_radius(
            starting_n=1, radius=r, repeat=repeats)[repeats-1][0])
    else:
        nList.append(-1)


nList_sliced = nList[2:]
rList_sliced = rList[2:]

for n, r in zip(nList_sliced, rList_sliced):
    print(n, r)
