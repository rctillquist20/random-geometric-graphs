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

# import multilateration as geo
# import math
# import time
G = nx.random_geometric_graph(23, radius=1, seed=1)
# start = time.perf_counter()
# print(geo.bruteForce(G))
# end = time.perf_counter()
# execution_time = (end - start)
# print("\nTime: ", execution_time, "\n\n")

# test= get_close_to_unique_columns(analysis.get_distance_matrix(G=G, display=True))
# print(test[0][1])
# decode.get_data(file_name="rgg_data_10.list")


offset = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=True))
print(offset)

# negatives, not isolated vertices pick rate?

# Why was 0 always picked in 294604 even though the others had the same offset (some did not even appear)?