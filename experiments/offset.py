import networkx as nx
import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
# from analysis import get_distance_matrix
import analysis
import decode
# Question: Will having the lowest / middle / highest (excluding isolated 
# vertices) offset to unique rows NODES GROUP be 
# always have 100% pick rate included in metric dimension tuple?


# Get close to not having the highest count common rows' value for an
# individual column and group those columns by
# the difference in the commonality of rows they may share with other columns
# in order to combine with isolated vertices to create R.
#
# close_to_unique Dictionary Format:
# {Highest count of common value shared based on rows of an individual column of value : columns index}
# Return: Close to unique rows Columns SORTED BY KEY
def get_close_to_unique_columns(matrix):
    close_to_unique = {}
    num_cols = len(matrix[0])

    for column in range(num_cols):
        value_counts = {}
        for row in matrix:
            value = row[column]
            value_counts[value] = value_counts.get(value, 0) + 1

        max_value = max(value_counts.values())

        if max_value in close_to_unique:
            close_to_unique[max_value].append(column)
        else:
            close_to_unique[max_value] = [column]

    return sorted(close_to_unique.items())

# import multilateration as geo
# import math
# import time
# G = nx.random_geometric_graph(23, radius=math.sqrt(2))
# start = time.perf_counter()
# print(geo.bruteForce(G))
# end = time.perf_counter()
# execution_time = (end - start)
# print("\nTime: ", execution_time, "\n\n")

# test= get_close_to_unique_columns(analysis.get_distance_matrix(G=G, display=True))
# print(test[0][1])
# decode.get_data(file_name="rgg_data_10.list")




# negatives, not isolated vertices pick rate?

# Why was 0 always picked in 294604 even though the others had the same offset (some did not even appear)?