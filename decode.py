from experiments import readList
import os.path
import networkx as nx
import matplotlib.pyplot as plt

# _10 for 10 repeats based on experiments.py

# file_name = 'rgg_data_10.list'

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

# IMPORTANT NOTE: MAKE SURE THE PARAMETER FOR FILE_NAME IS SPECIFIED!!

def get_data(nodes=None, radius=None, seed=None, r_set=None,
             execution_time=None, sort_by=None, ascending=True, output=False, image=False, file_name='no_name_'):

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

        n_seeds = []
        for item in filtered_data:
            if output == True:
                print('\nNodes: ', item[0])
                print('Radius: ', item[1])
                print('Seed: ', item[2])
                G = nx.random_geometric_graph(
                    n=int(item[0]), radius=float(item[1]), seed=int(item[2]))
                # print('Edges: ', nx.number_of_edges(G))
                # print('Resolving Set: ', item[3])
                # print('Execution Time: ', item[4])
                # print('\nPositions: ', item[5], '\n')
                if image == True:
                    plt.figure(figsize=(7, 7))
                    plt.title(f"Nodes: {item[0]}, Radius: {item[1]}, Seed: {item[2]}, Edges: {nx.number_of_edges(G)}")
                    color_map = []
                    for node in G:
                        if node in item[3]:
                            color_map.append('red')
                        else:
                            color_map.append('cyan')
                    nx.draw(G, pos=item[5], with_labels=True, font_weight='bold',
                            node_color=color_map, edge_color='black')

                    # CHANGE HERE FOR DIFFERENT REPEATS FOLDER!!!
                    # data_num = 10
                    # os.makedirs(f'data_images/data_{data_num}', exist_ok=True)
                    # plt.savefig(
                    #     f"data_images/data_{data_num}/graph_{item[0]}_{item[1]}_{item[2]}.png")
                # n_seeds.append(item[2])
        # print('\n')
        return filtered_data
        # return n_seeds
    except:
        print('Error: Can not decode and read file.')
        return None

nodes = 10
radius = 0.4000000000000001
seed = 294604
# seed_list = [267652, 289604, 437162, 439468, 614008, 628768, 657341, 726260, 763785, 852397]
# static_positions = []

get_data(sort_by=True, ascending=False, file_name = 'rgg_data.list')
# for seed in seed_list:
#     static_positions.append(get_data(nodes = 34, radius=0.2, seed=seed, output=False)[5])

# print('\n')
# print(static_positions, '\n')
# seed_list = get_data(nodes=nodes, radius=radius, output=False)
# print(sorted(seed_list))


###### Figure for ICH vs Random vs GeoHAT #####

def calculate_average(numbers):
    if not numbers:
        return 0

    total = sum(numbers)
    average = total / len(numbers)
    return average

# nodes = [34, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10]
# r_list = [0.2, 0.30000000000000004, 0.4000000000000001, 0.5000000000000001, 0.6000000000000001, 0.7000000000000002, 0.8000000000000003, 0.9000000000000001, 1.0000000000000002, 1.1000000000000003, 1.2000000000000004]

# data = []
# for n, r in zip(nodes, r_list):
#     ich = get_data(sort_by=True, ascending=True, file_name='rgg_data_10_ich.list', output=False, nodes=n, radius=r)
#     average = []
#     for i in ich:
#         average.append(len(i[3]))
#     ich_avg = calculate_average(average)


#     ran = get_data(sort_by=True, ascending=True, file_name='rgg_data_10_random.list', output=False, nodes=n, radius=r)
#     average = []
#     for i in ran:
#         average.append(len(i[3]))
#     ran_avg = calculate_average(average)

#     geo = get_data(sort_by=True, ascending=True, file_name='rgg_data_10_random.list', output=False, nodes=n, radius=r)
#     average = []
#     for i in geo:
#         average.append(len(i[3]))
#     geo_avg = calculate_average(average)
#     data.append((n, [ich_avg, ran_avg, geo_avg], r))


# import matplotlib.pyplot as plt
# import numpy as np

# # Extract data
# nodes, metric_dimensions, radii = zip(*data)

# # Number of bars at each x-axis location
# n_bars = len(metric_dimensions[0])

# # Get the width of the bars
# bar_width = 0.25

# # Positions of the bars on the x-axis
# x = np.arange(len(nodes))

# # Create the plot
# fig, ax = plt.subplots()

# legend_labels = ["ICH", "Random", "GeoHAT"]

# # Create the bars
# for i in range(n_bars):
#     offset = (i - n_bars / 2) * bar_width
#     plt.bar(x + offset, [md[i] for md in metric_dimensions], width=bar_width, label=legend_labels[i])

# x_labels = [f"{n} | {r:.2f}" for n, r in zip(nodes, radii)]


# # Add labels, title, and legend
# plt.xlabel("Nodes |  Radius")
# plt.ylabel("Average Metric Dimension Count")
# plt.title("ICH vs Random vs GeoHAT (10 Different Graph Seeds)")
# plt.xticks(x, x_labels)
# plt.legend()

# plt.show()
