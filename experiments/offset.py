import networkx as nx
import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
# from analysis import get_distance_matrix
import analysis
import decode
# Question: Will having the lowest / middle / highest (excluding isolated 
# vertices) offset to unique rows NODES GROUP be 
# always have 100% pick rate included in metric dimension tuple?

# Finds the element with the highest count in a specific matrix row array so 
# can get the highest offset.
def get_element_with_highest_count(array):
    count_dict = {}
    for element in array:
        count_dict[element] = count_dict.get(element, 0) + 1
    max_count = max(count_dict.values())

    return max_count

# # Example usage
# arr = [1, 2, 3, 2, 2, 4, 4, 4, 5]
# result = get_element_with_highest_count(arr)
# print(result)  # Output: 3

# Get close to not having the highest count common rows' value for an
# individual column and group those columns by
# the difference in the commonality of rows they may share with other columns
# in order to combine with isolated vertices to create R.
#
# close_to_unique Dictionary Format:
# {Highest count of common value shared based on rows of an individual column of value : columns index}
# Return: Close to unique rows Columns SORTED BY KEY
def get_close_to_unique_rows_offset(matrix):
    offset = {}

    for row_index, row in enumerate(matrix):
        offset.setdefault(get_element_with_highest_count(row), []).append(row_index)

    return dict(sorted(offset.items()))

# Helps us get the highest offset.
def get_highest_key(dictionary):
    if not dictionary:
        return None

    max_key = max(dictionary, key=dictionary.get)
    return max_key

# Helps us get the lowest offset.
def get_lowest_key(dictionary):
    if not dictionary:
        return None

    min_key = min(dictionary, key=dictionary.get)
    return min_key


# import multilateration as geo
# import math
# import time
# G = nx.random_geometric_graph(n=10, radius=0.09, seed=897200)
# start = time.perf_counter()
# print(geo.bruteForce(G))
# end = time.perf_counter()
# execution_time = (end - start)
# print("\nTime: ", execution_time, "\n\n")

# test= get_close_to_unique_columns(analysis.get_distance_matrix(G=G, display=True))
# print(test[0][1])
# decode.get_data(file_name="rgg_data_10.list")


# offset = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=True))
# print(offset)
# print(get_highest_key(offset))
# print(get_lowest_key(offset))

# decode.get_data(file_name='comeback_1_10.list', nodes=10,output=True)


from matplotlib import pyplot as plt
import multilateration as geo
import numpy as np
### Create Experiment of x-axis = seeds (lowest to highest sorted) | y-axis = true/false (1/0) in Bruteforce Metric Dimension.
nodes = 10
radius = 0.9
# plt.title(f'A column of the Lowest Offset always a part of the Metric Dimension? (N = {nodes}, R = {radius})')
seed_list = sorted(decode.get_seeds(file_name='comeback_1_10.list', nodes=10))
probability_list = []
for seed in seed_list:
    G = nx.random_geometric_graph(n=nodes, radius=radius, seed=int(seed))
    r_sets = geo.bruteForce(G,numSets=-1)
    offset_in_r_set = 0
    for set_ in r_sets:
        if 0 in set_:
            offset_in_r_set += 1
    probability_list.append(offset_in_r_set / len(r_sets))

### USING BAR CHARTS ###
plt.figure(figsize=(9, 6))
plt.xlabel('Seeds')
plt.ylabel('Probability')
plt.title(f'A column of the Lowest Offset always a part of the Metric Dimension? (N = {nodes}, Radius = {radius})')
plt.ylim(0, 1)  # Set y-axis limits to 0 and 1
plt.xticks(range(len(seed_list)), seed_list)  # Set x-axis labels to seed names
plt.bar(range(len(seed_list)), probability_list, width=0.5)
plt.show()

### USING PRINT OUT TABLE ###
import pandas as pd
data = {'Seeds': seed_list, 'Probability': probability_list}
df = pd.DataFrame(data)
print(df)

# negatives, not isolated vertices pick rate?

# Why was 0 always picked in 294604 even though the others had the same offset (some did not even appear)?