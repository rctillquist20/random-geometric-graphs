import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
import geohat
## Metric Dimension EXISTS
# matrix = [
#     [1, 2, -1, 0],
#     [1, 0, 0, -1],
#     [2, 8, -1, -1]
# ]

matrix = [[0, 1, 2, 1, 2, 3],
[1, 0, 1, 1, 1, 2],
[2, 1, 0, 2, 2, 1],
[1, 1, 2, 0, 2, 3],
[2, 1, 2, 2, 0, 3],
[3, 2, 1, 3, 3, 0]]
[0, 2]

# print(geohat.is_resolving_set(matrix, [0, 2]))
from collections import Counter

def most_common_value(arr):
  count = Counter(arr)
  return count.most_common(1)[0][0]

def get_column(column_index, matrix):
    column = [row[column_index] for row in matrix]
    return column

def find_index(arr, element):
  try:
    return arr.index(element)
  except ValueError:
    return False


def geopigeon(nodes, matrix):
    increment_num = 1
    for i in range((nodes//2)):
        r_set = []
        for row in matrix:
            most_common = most_common_value(row)
            pick_column_up_1 = most_common+increment_num
            pick_column_down_1 = most_common-increment_num
            if pick_column_up_1 in row:
                column = find_index(row, pick_column_up_1)
                if column == False:
                    column = find_index(row, pick_column_down_1)
                    if column == False:
                        return False
                r_set.append(column)
            geohat.is_resolving_set(matrix, r_set)
        increment_num += 1
    return False

import time
def get_stats_geopigeon(nodes, matrix):
    start = time.perf_counter()
    r_set = geopigeon(nodes, matrix)
    end = time.perf_counter()
    execution_time = (end - start)
    return r_set, execution_time

# print(geopigeon(6, matrix))
# nodes = 6
# print(get_stats_geopigeon(nodes, matrix))