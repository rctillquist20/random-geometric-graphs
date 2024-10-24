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


def is_pair_in_r_set(items, items2, r_sets):
    for node in items:
            for node2 in items2:
                for tuple in r_sets:
                    if (node in tuple) and (node2 in tuple):
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


### Dataset 2
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Highest')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lowest')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Median', round='Ceil')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Median', round='Floor')

# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Upper Quartile', round='Floor', method='Inclusive')

# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list", filename="2", mode='Lower Quartile', round='Floor', method='Inclusive')

# ### Dataset 3
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Highest')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lowest')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Median', round='Ceil')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Median', round='Floor')

# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Upper Quartile', round='Floor', method='Inclusive')

# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_3_1_repeat_3_to_23nodes_200graphs.list", filename="3", mode='Lower Quartile', round='Floor', method='Inclusive')

# ### Dataset 4
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Highest')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lowest')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Median', round='Ceil')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Median', round='Floor')

# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Upper Quartile', round='Floor', method='Inclusive')

# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Ceil', method='Exclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Ceil', method='Inclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Floor', method='Exclusive')
# is_type_in_r(datalist="comeback_4_1_repeat_3_to_23nodes_200graphs.list", filename="4", mode='Lower Quartile', round='Floor', method='Inclusive')


## Is AT LEAST TWO type offset pairs within R sets? ##
#
# PURPOSE: Calculate success of offset nodes of Five-number summary!!!
def offset_pairs(datalist, filename, mode, mode2, method='', round='',  method2='', round2=''):
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

    # for node, radius, seed in zip(all_nodes, all_r, all_seeds):
    #     print(mode + ' ' + mode2)
    # return

    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        # if mode == 'Highest' and mode2 == 'Ceil Median':
        #     print("\n\n\n\nSUCCESS!!!\n\n\n\n")
        #     return
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
            quit()
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


        if mode2 == 'Highest':
            key2 = get_highest_key(offset_dict)
        elif mode2 == 'Lowest':
            key2 = get_lowest_key(offset_dict)
        elif mode2 == 'Median':
            key2 = get_median_key(offset_dict)
        elif (mode2 == 'Upper Quartile') and (method2 == 'Exclusive') or (method2 == 'Inclusive'):
            key2 = get_upper_quartile_key(offset_dict, method=method2)
        elif (mode2 == 'Lower Quartile') and (method2 == 'Exclusive') or (method2 == 'Inclusive'):
            key2 = get_lower_quartile_key(offset_dict, method=method2)
        else:
            print('Error: No valid mode selected.')
            return
        if (is_float(key2) != False) or (key2 not in offset_dict.keys()):
            
            if round2 == 'Ceil':
                ##### IMPORTANT #####
                ### Ceil Setting ###
                items2 = get_ceil_desired_key(offset_dict = offset_dict, offset_key =  key2)
            elif round2 == 'Floor':    
                ### Floor Setting ###
                items2 = get_floor_desired_key(offset_dict = offset_dict, offset_key = key2)
        
        else:
            items2 = offset_dict[key2]
    
        result = is_pair_in_r_set(items, items2, r_sets)
        # count += 1
        # print(count)
        if result == True:
            true_count += 1
        else:
            false_count += 1

    ### IMPORTANT ###
    with open(f'/Users/evanalba/random-geometric-graphs/images/offset/tests/offset_pairs/{filename}.txt', 'a') as file:
        total_graphs = 200  ## IMPORTANT
        percentage = (true_count/total_graphs) * 100

        if (((round == 'Ceil') or (round == 'Floor')) and ((method == 'Exclusive') or (method == 'Inclusive'))) or (((round2 == 'Ceil') or (round2 == 'Floor')) and ((method2 == 'Exclusive') or (method2 == 'Inclusive'))):
            file.write(f'\n\n{round} {method} {mode} and {round2} {method2} {mode2}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')
        elif ((round == 'Ceil') or (round == 'Floor')) or ((round2 == 'Ceil') or (round2 == 'Floor')):
            file.write(f'\n\n{round} {mode} and {round2} {mode2}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')
        else:
            file.write(f'\n\n{mode} and {mode2}:\nTrue: {true_count}\nFalse: {false_count}\nProbability of being True: {percentage}%')


modes = ['Highest', 'Lowest', 'Median', 'Median', 'Upper Quartile', 
         'Upper Quartile', 'Upper Quartile', 'Upper Quartile', 
         'Upper Quartile', 'Lower Quartile', 'Lower Quartile', 
         'Lower Quartile', 'Lower Quartile']
rounds = ['Ceil', 'Floor']
quans = ['Exclusive', 'Inclusive']
datasets = ['comeback_2_1_repeat_3_to_23nodes_200graphs.list', 'comeback_3_1_repeat_3_to_23nodes_200graphs.list', 
            'comeback_4_1_repeat_3_to_23nodes_200graphs.list']
filenames = ['2', '3', '4']

for d, f in zip(datasets, filenames):
    test = []
    seen = []
    m1_final = ''
    for m in modes:
        seen2 = []

        r_final = ''
        q_final = ''
        # Set up the 1st var that will iterate through all m2 vars.
        if m in ['Median', 'Upper Quartile', 'Lower Quartile']:
            for r in rounds:
                if (m == 'Median') and ((r + ' ' + m) not in seen):
                    seen.append(r + ' ' + m)
                    m1_final = r + ' ' + m
                    r_final = r
                    # test.append(m1_final)
                    break

                is_done = False
                if (m == 'Upper Quartile') or (m == 'Lower Quartile'):
                    for q in quans:
                        if (r + ' ' + q + ' ' + m) not in seen:
                            seen.append(r + ' ' + q + ' ' + m)
                            m1_final = r + ' ' + q + ' ' + m
                            r_final = r
                            q_final = q
                            # test.append(m1_final)
                            is_done = True
                            break
                if is_done == True:
                    break
        else:
            m1_final = m # If Highest or Lowest keep it as is.

    
        for m2 in modes:
            if m == m2:
                continue


            r2_final = ''
            q2_final = ''
            if m2 in ['Median', 'Upper Quartile', 'Lower Quartile']:
                is_done = False
                for r in rounds:
                    if (m2 == 'Median') and ((r + ' ' + m2) not in seen2):
                            seen2.append(r + ' ' + m2)
                            m2_final = r + ' ' + m2
                            r2_final = r
                            
                            break
                    for q in quans:
                        if ((m2 == 'Upper Quartile') or (m2 == 'Lower Quartile')) and ((r + ' ' + q + ' ' + m2) not in seen2):
                            seen2.append(r + ' ' + q + ' ' + m2)
                            m2_final = r + ' ' + q + ' ' + m2
                            r2_final = r
                            q2_final = q
                            
                            is_done = True
                            break
                    if is_done == True:
                        break
            else:
                m2_final = m2
  
            if ([m1_final, m2_final] in test) or ([m2_final, m1_final] in test):
                continue
            else:
                test.append([m1_final, m2_final])
                offset_pairs(datalist=d, filename=f, mode=m, mode2=m2, method=q_final, round=r_final,  method2=q2_final, round2=r2_final)

    
    # print(test)
    # print(len(test))



            # offset_pairs(datalist=d, filename=f, mode=m1_final, mode2=m2_final, method='', round='',  method2='', round2='')

