import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
import analysis
import decode
import networkx as nx
from matplotlib import pyplot as plt
import multilateration as geo
import numpy as np
import math
import statistics


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


def get_close_to_unique_rows_offset(matrix):
    offset = {}

    for row_index, row in enumerate(matrix):
        offset.setdefault(get_element_with_highest_count(row), []).append(row_index)

    return dict(sorted(offset.items()))
