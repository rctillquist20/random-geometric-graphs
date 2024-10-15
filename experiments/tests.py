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

# Helps us get the lowest offset dictionary key.
def get_lowest_key(dictionary):
    if not dictionary:
        return None

    min_key = min(dictionary, key=dictionary.get)
    return min_key


def is_float(value):
  try:
    float_value = float(value)
    return float_value != int(float_value)
  except ValueError:
    return False


def count_elements_in_array_of_tuples(array):
  count = 0
  for tuple in array:
    count += len(tuple)
  return count


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


def get_ceil_desired_key(offset_dict, offset_key):
    ## Ceil Setting ##
    desired_offset_key = int(math.ceil(offset_key))
    if desired_offset_key not in offset_dict.keys():
        for key in offset_dict.keys():
            if key > desired_offset_key:
                desired_offset_key = key
                break

    # NOTE: If we can not find a valid ceil key preferred, we will try
    # getting the floor key instead. Same goes with Floor preferred
    # first method.
    try:
        offset_items = offset_dict[desired_offset_key]
    except KeyError:
        if desired_offset_key not in offset_dict.keys():
            for key in reversed(offset_dict.keys()):
                if key < desired_offset_key:
                    desired_offset_key = key
                    return offset_dict[desired_offset_key]
    else:
        return offset_items
    

def get_floor_desired_key(offset_dict, offset_key):
    ## Floor Setting ##
    desired_offset_key = int(math.floor(offset_key))
    if desired_offset_key not in offset_dict.keys():
        for key in reversed(offset_dict.keys()):
            if key < desired_offset_key:
                desired_offset_key = key
                break
    
    try:
        offset_items = offset_dict[desired_offset_key]
    except KeyError:
        if desired_offset_key not in offset_dict.keys():
            for key in offset_dict.keys():
                if key > desired_offset_key:
                    desired_offset_key = key
                    return offset_dict[desired_offset_key]
    else:
        return offset_items


def get_upper_quartile_key(dictionary, method):
  if (method == "exclusive") or (method == "inclusive"):
    values = list(dictionary.keys())
    if len(values) > 1:
        upper_quartile = 2
        return statistics.quantiles(values, n=4, method=f"{method}")[upper_quartile]
    return values[0]
 
  print("Error: Quantile method not exclusive or inclusive.")
  quit()


def is_r_set(low_items, offset_items, r_sets):
    for low_offset_node in low_items:
            for upper_quartile_offset_node in offset_items:
                for tuple in r_sets:
                    if (low_offset_node in tuple) and (upper_quartile_offset_node in tuple):
                        return True
    return False


# TEST 1: Is there at least 1 r set that contains the lowest and Ceil Exclusive Upper 
# Quartile?

def test1(datalist, filename):
    true_count = 0
    false_count = 0
    count = 0

    all_nodes = decode.get_items_list(file_name=f'{datalist}', nodes=True)
    # Make sure the file has the total of N number of graphs wanted...
    print(len(all_nodes))
    print(max(all_nodes))
    return
    all_r = decode.get_items_list(file_name=f'{datalist}', radius=True)
    all_seeds = decode.get_items_list(file_name=f'{datalist}', seed=True)

    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        r_sets = geo.bruteForce(G, numSets=-1)

        ## Note: Offset_dict keys are SORTED!!!
        offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
        
      
        low_offset_key = get_lowest_key(offset_dict)
        low_items = offset_dict[low_offset_key]
        upper_quartile_offset_key = get_upper_quartile_key(offset_dict, method="exclusive")
        if (is_float(upper_quartile_offset_key) != False) or (upper_quartile_offset_key not in offset_dict.keys()):
            
            ##### IMPORTANT #####
            ### Ceil Setting ###
            offset_items = get_ceil_desired_key(offset_dict = offset_dict, offset_key =  upper_quartile_offset_key)
            
            ### Floor Setting ###
            #offset_items = get_floor_desired_key(offset_dict = offset_dict, offset_key = desired_offset_key)
        
        else:
            offset_items = offset_dict[upper_quartile_offset_key]

        result = is_r_set(low_items, offset_items, r_sets)
        # count += 1
        # print(count)
        if result == True:
            true_count += 1
        else:
            false_count += 1

    with open(f'/Users/evanalba/random-geometric-graphs/images/offset/tests/test1/{filename}.txt', 'a') as file:
        file.write(f'\nTrue: {true_count}\nFalse: {false_count}')

test1(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2")
# test1(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3")
# test1(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4")


def offset_pairs(datalist, filename, mode):
    true_count = 0
    false_count = 0

    all_nodes = decode.get_items_list(file_name=f'{datalist}', nodes=True)
    all_r = decode.get_items_list(file_name=f'{datalist}', radius=True)
    all_seeds = decode.get_items_list(file_name=f'{datalist}', seed=True)

    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        # if (node != 20):
        #     continue
        # Round due to median being like 5.5
        round = False
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        r_sets = geo.bruteForce(G, numSets=-1)

        ## Note: Offset_dict keys are SORTED!!!
        offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
        
      
        low_offset_key = get_lowest_key(offset_dict)
        low_items = offset_dict[low_offset_key]
        upper_quartile_offset_key = get_upper_quartile_key(offset_dict, method="exclusive")
        if (is_float(upper_quartile_offset_key) != False) or (upper_quartile_offset_key not in offset_dict.keys()):
            round = True
            # print(desired_offset_key)
            
            ##### IMPORTANT #####
            ### Ceil Setting ###
            offset_items = get_ceil_desired_key(offset_dict = offset_dict, offset_key =  upper_quartile_offset_key)
            
            ### Floor Setting ###
            #offset_items = get_floor_desired_key(offset_dict = offset_dict, offset_key = desired_offset_key)
        
        else:
            offset_items = offset_dict[upper_quartile_offset_key]

        result = is_r_set(low_items, offset_items, r_sets)
        if result == True:
            true_count += 1
        else:
            false_count += 1
        with open(f'/Users/evanalba/random-geometric-graphs/images/offset/tests/offset_pairs/{filename}.txt', 'a') as file:
            file.write(f'\n{node} | {radius} | {seed} |: {result}')
        break
    
    with open(f'/Users/evanalba/random-geometric-graphs/images/offset/tests/offset_pairs/{filename}.txt', 'a') as file:
        file.write(f'\n\n{mode}\n\nTotal Offset Pair Score:\nTrue: {true_count}\nFalse: {false_count}')

# offset_pairs(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="pig")