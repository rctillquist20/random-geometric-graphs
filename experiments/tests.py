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

def get_close_to_unique_rows_offset(matrix):
    offset = {}

    for row_index, row in enumerate(matrix):
        offset.setdefault(get_element_with_highest_count(row), []).append(row_index)

    return dict(sorted(offset.items()))

# Helps us get the highest offset dictionary key.
def get_highest_key(dictionary):
    if not dictionary:
        return None

    max_key = max(dictionary, key=dictionary.get)
    return max_key

# Helps us get the lowest offset dictionary key.
def get_lowest_key(dictionary):
    if not dictionary:
        return None

    min_key = min(dictionary, key=dictionary.get)
    return min_key

def get_lowest_and_least_common_count(dictionary):
    lowest = get_lowest_key(dictionary)
    dictionary.get(lowest)


def get_median_key(dictionary):
    keys = list(dictionary.keys())
   
    median_key = statistics.median(keys)
    return median_key


def get_upper_quartile_key(dictionary, method):
  method = method.lower()
  if (method == "exclusive") or (method == "inclusive"):
    values = list(dictionary.keys())
    if len(values) > 1:
        upper_quartile = 2
        return statistics.quantiles(values, n=4, method=f"{method}")[upper_quartile]
    return values[0]
 
  print("Error: Quantile method not exclusive or inclusive.")
  quit()


def get_lower_quartile_key(dictionary, method):
  method = method.lower()
  if (method == "exclusive") or (method == "inclusive"):
    values = list(dictionary.keys())
    if len(values) > 1:
        lower_quartile = 0
        return statistics.quantiles(values, n=4, method=f"{method}")[lower_quartile]
    return values[0]

  print("Error: Quantile method not exclusive or inclusive.")
  quit()


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


def type_in_r(items, r_sets):
    for node in items:
            for tuple in r_sets:
                if node in tuple:
                    return True
    return False

# TEST 1: Is there at least 1 r set that contains the lowest and Ceil Exclusive Upper 
# Quartile?

def test1(datalist, filename):
    true_count = 0
    false_count = 0
    # count = 0

    all_nodes = decode.get_items_list(file_name=f'{datalist}', nodes=True)
    # Make sure the file has the total of N number of graphs wanted...
    # print(len(all_nodes))
    # print(max(all_nodes))
    # return
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

# test1(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2")
# test1(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3")
# test1(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4")


## Is AT LEAST ONE type offset node within R sets? ##
#
# PURPOSE: Calculate success of offset nodes of Five-number summary!!!
def is_type_in_r(datalist, filename, mode, method='', round=''):
    true_count = 0
    false_count = 0
    # count = 0

    all_nodes = decode.get_items_list(file_name=f'{datalist}', nodes=True)
    # Make sure the file has the total of N number of graphs wanted...
    # print(len(all_nodes))
    # print(max(all_nodes))
    # return
    all_r = decode.get_items_list(file_name=f'{datalist}', radius=True)
    all_seeds = decode.get_items_list(file_name=f'{datalist}', seed=True)

    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        r_sets = geo.bruteForce(G, numSets=-1)

        ## Note: Offset_dict keys are SORTED!!!
        offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
        
        if mode == 'Highest':
            key = get_highest_key(offset_dict)
        elif mode == 'Lowest':
            key = get_lowest_key(offset_dict)
        elif mode == 'Median':
            key = get_median_key(offset_dict)
        elif (mode == 'Upper Quartile') and (method == 'Exclusive') or (method == 'Inclusive'):
            key = get_upper_quartile_key(offset_dict, method=method)
        elif (mode == 'Lower Quartile') and (method == 'Exclusive') or (method == 'Inclusive'):
            key = get_lower_quartile_key(offset_dict, method=method)
        else:
            print('Error: No valid mode selected.')
            return
        if (is_float(key) != False) or (key not in offset_dict.keys()):
            
            if round == 'Ceil':
                ##### IMPORTANT #####
                ### Ceil Setting ###
                items = get_ceil_desired_key(offset_dict = offset_dict, offset_key =  key)
            elif round == 'Floor':    
                ### Floor Setting ###
                items = get_floor_desired_key(offset_dict = offset_dict, offset_key = key)
        
        else:
            items = offset_dict[key]

        result = type_in_r(items, r_sets)
        # count += 1
        # print(count)
        if result == True:
            true_count += 1
        else:
            false_count += 1

    with open(f'/Users/evanalba/random-geometric-graphs/images/offset/tests/is_type_in_r/{filename}.txt', 'a') as file:
        total_graphs = 200  ## IMPORTANT
        percentage = (true_count/total_graphs) * 100
        if (round == 'Ceil') or (round == 'Floor') and (method == 'Exclusive') or (method == 'Inclusive'):
            file.write(f'\n{round} {method} {mode}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')
        elif (round == 'Ceil') or (round == 'Floor'):
            file.write(f'\n{round} {mode}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')
        else:
            file.write(f'\n{mode}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')

### Dataset 2
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Highest')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lowest')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Median', round='Ceil')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Median', round='Floor')

is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Floor', method='Inclusive')

is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Floor', method='Inclusive')

### Dataset 3
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Highest')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lowest')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Median', round='Ceil')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Median', round='Floor')

is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Floor', method='Inclusive')

is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Floor', method='Inclusive')

### Dataset 4
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Highest')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lowest')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Median', round='Ceil')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Median', round='Floor')

is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Floor', method='Inclusive')

is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Ceil', method='Exclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Ceil', method='Inclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Floor', method='Exclusive')
is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Floor', method='Inclusive')


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