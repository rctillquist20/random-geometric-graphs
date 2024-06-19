from experiments import readList
import os.path
import networkx as nx
import matplotlib.pyplot as plt


file_name = 'rgg_data_10.list'

# Returns data that can be filter based on what what we collected so can
# analyze it.
# Parameters:
# - nodes
# - radius
# - seed
# - r_set (Resolving Set)
# - execution time (Time in seconds)
# - sort_by
# - ascending (data) Default: True
# - output (Displays information about data on file.) Default: True


def get_data(nodes=None, radius=None, seed=None, r_set=None,
             execution_time=None, sort_by=None, ascending=True, output=True, image=False):

    if not os.path.isfile(file_name):
        print('Error: File does not exist.')
        return None

    try:
        data_list = readList(file_name)

        filtered_data = [item for item in data_list if
                         (nodes is None or item[0] == nodes) and
                         (radius is None or item[1] == radius) and
                         (seed is None or item[2] == seed) and
                         (r_set is None or item[3] == r_set) and
                         (execution_time is None or item[4] == execution_time)]

        if sort_by is not None:
            def sort_by_item(item):
                return item[sort_by]
            filtered_data.sort(key=sort_by_item, reverse=not ascending)

        for item in filtered_data:
            if output == True:
                print('\nNodes: ', item[0])
                print('Radius: ', item[1])
                print('Seed: ', item[2])
                G = nx.random_geometric_graph(
                    n=int(item[0]), radius=float(item[1]), seed=int(item[2]))
                print('Edges: ', nx.number_of_edges(G))
                print('Resolving Set: ', item[3])
                print('Execution Time: ', item[4])
                print('\nPositions: ', item[5], '\n')
                if image == True:
                    plt.figure(figsize=(7, 7))
                    plt.title(f"Nodes: {item[0]}, Radius: {item[1]}, Seed: {item[2]}")
                    color_map = []
                    for node in G:
                        if node in item[3]:
                            color_map.append('red')
                        else:
                            color_map.append('cyan')
                    nx.draw(G, pos=item[5], with_labels=True, font_weight='bold',
                            node_color=color_map, edge_color='black')
                    
                    # CHANGE HERE FOR DIFFERENT REPEATS FOLDER!!!
                    data_num = 10
                    os.makedirs(f'data_images/data_{data_num}', exist_ok=True)
                    plt.savefig(f"data_images/data_{data_num}/graph_{item[0]}_{item[1]}_{item[2]}.png")

            else:
                return item
        # print('\n')
        return item
    except:
        print('Error: Can not decode and read file.')
        return None


nodes = 10
radius = 1.5000000000000004
seed = 278880

get_data(sort_by=True, ascending=True, image=True)
# get_data(nodes=nodes, radius=radius, seed=seed, image=True)
