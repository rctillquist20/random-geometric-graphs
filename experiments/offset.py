import networkx as nx
import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
# from analysis import get_distance_matrix
import analysis
import decode
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


def get_lower_quartile_key(dictionary):
    pass


def get_upper_quartile_key(dictionary):
    pass

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

def count_integer_in_array_of_tuples(array, target_integer):
  count = 0
  for tuple in array:
    count += tuple.count(target_integer)
  return count

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
### IMPORTANT ###
# nodes = 10
# radius = 0.9
# # desired_offset = 0
# # plt.title(f'A column of the Lowest Offset always a part of the Metric Dimension? (N = {nodes}, R = {radius})')
# all_r = list(np.arange(0.02, 0.14, 0.01)) + \
#         list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))
# all_seeds = list(range(3, 23))
# total_offset_probability = []
# for n, r in zip(all_seeds, all_r):
#     nodes = n
#     radius = r
#     seed_list = sorted(decode.get_seeds(file_name='comeback_2_1_repeat_3_to_23nodes_200graphs.list', nodes=n)) 
#     # NOTE: If Random Graphs with RANDOM NODES AND RANDOM RADIUS CHANGE UP THE CODE!!!
#     probability_list = []
    
#     # Round due to median being like 5.5
#     round = False
#     for seed in seed_list:
#         G = nx.random_geometric_graph(n=nodes, radius=radius, seed=int(seed))
#         r_sets = geo.bruteForce(G, numSets=-1)
#         offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
        
#         ### IMPORTANT: OFFSET SETTINGS TESTING ###   
#         # print(offset_dict)
#         desired_offset_key = get_highest_key(offset_dict) ## CHANGE IF GETTING DIFFERENT OFFSET
#         if (is_float(desired_offset_key) != False) or (desired_offset_key not in offset_dict.keys()):
#             round = True
#             import math
#             desired_offset_key = int(math.ceil(desired_offset_key))
#             # # Ceil Setting ##
#             # if desired_offset_key not in offset_dict.keys():
#             #     for key in offset_dict.keys():
#             #         if key > desired_offset_key:
#             #             desired_offset_key = key
#             #             break
            
#             # Floor Setting ##
#             if desired_offset_key not in offset_dict.keys():
#                 for key in reversed(offset_dict.keys()):
#                     if key < desired_offset_key:
#                         desired_offset_key = key
#                         break

#             offset_items = offset_dict[desired_offset_key]
#         else:
#             offset_items = offset_dict[desired_offset_key]

#         offset_found = 0
#         for set_ in r_sets:
#             for item in offset_items:
#                 if item in set_:
#                     offset_found += 1
#                     break
#         probability_list.append(offset_found / len(r_sets))
#     total_offset_probability.append(sum(probability_list))



# def get_offset_probability(mode):
#     # NOTE: If Random Graphs with RANDOM NODES AND RANDOM RADIUS CODE HERE!!!
 
#     all_nodes = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', nodes=True)
#     all_r = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', radius=True)
#     all_seeds = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', seed=True)
#     total_offset_probability = []
#     for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        
#         # Round due to median being like 5.5
#         round = False
#         G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
#         r_sets = geo.bruteForce(G, numSets=-1)
#         offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
            
#         ### IMPORTANT: OFFSET SETTINGS TESTING ###   
#         # print(offset_dict)
#         desired_offset_key = get_median_key(offset_dict) ## CHANGE IF GETTING DIFFERENT OFFSET
#         if (is_float(desired_offset_key) != False) or (desired_offset_key not in offset_dict.keys()):
#             round = True
#             import math
#             desired_offset_key = int(math.ceil(desired_offset_key))
#             # Ceil Setting ##
#             # if desired_offset_key not in offset_dict.keys():
#             #     for key in offset_dict.keys():
#             #         if key > desired_offset_key:
#             #             desired_offset_key = key
#             #             break
            
#             # Floor Setting ##
#             if desired_offset_key not in offset_dict.keys():
#                 for key in reversed(offset_dict.keys()):
#                     if key < desired_offset_key:
#                         desired_offset_key = key
#                         break

#             offset_items = offset_dict[desired_offset_key]
#         else:
#             offset_items = offset_dict[desired_offset_key]

#         offset_found = 0
#         for set_ in r_sets:
#             for item in offset_items:
#                 if item in set_:
#                     offset_found += 1
#                     break
#         total_offset_probability.append(offset_found / len(r_sets))
#     with open('/Users/evanalba/random-geometric-graphs/images/offset/offset_types_4.txt', 'a') as file:
#         file.write(f'\n{mode}: {str(sum(total_offset_probability))}')

# get_offset_probability("Floor median")

# Radius affects offset probability or what??
# Lowest Offset node seems to be starting, but which one??
# Around the Median offset seems to be 2nd best pick.

#     ### USING BAR CHARTS ###
#     plt.figure(figsize=(9, 6))
#     plt.xlabel('Seeds')
#     plt.ylabel('Probability')
#     ### IMPORTANT: CHANGE TITLE ###
# mode = "Highest"
#     if round == True:
#         plt.title(f'Median Offset node(s) always a part of the Metric Dimension? (N = {nodes}, Radius = {radius})\nNote: Median is {mode}ed. If you can not get median offset key, go down to the next lowest key. ')
#     else: 
#         plt.title(f'{mode} Offset node(s) always a part of the Metric Dimension? (N = {nodes}, Radius = {radius})')
#     plt.ylim(0, 1.1)  # Set y-axis limits to 0 and 1
#     plt.xticks(range(len(seed_list)), seed_list)  # Set x-axis labels to seed names

#     # Create bars with probability values on top
#     bars = plt.bar(range(len(seed_list)), probability_list, width=0.5)
#     for bar, value in zip(bars, probability_list):
#         plt.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f'{value:.2f}', ha='center')
#     # plt.show()

#     ### IMPORTANT ###
#     if round == True:
#         save_dir = "/Users/evanalba/random-geometric-graphs/images/offset/median/floor"
#     else:
#         save_dir = f"/Users/evanalba/random-geometric-graphs/images/offset/median"

#     file_name = f"{nodes}_{radius}.jpg"
#     plt.savefig(f"{save_dir}/{file_name}")

# with open('/Users/evanalba/random-geometric-graphs/images/offset/offset_types_2.txt', 'a') as file:
#     file.write(f'\n{mode}: {str(sum(total_offset_probability))}')

### USING PRINT OUT TABLE ###
# import pandas as pd
# data = {'Seeds': seed_list, 'Probability': probability_list}
# df = pd.DataFrame(data)
# print(df)


### Note: sum(probability of each graph seed) / Total 190 Graphs (Each Graph Seed == 1, Graph Family = 10) (22 - 3) * 10 = 190
## NOTE: Bar Graph Compare types of offsets: highest, lowest, ceil median, floor median. ##
def get_offset_comparison(probability_list=[], file_name=""):
    

    plt.figure(figsize=(9, 6))
    plt.xlabel('Offset Types')
    plt.ylabel('Probability')
    plt.title('Highest vs Lowest vs Ceil median vs Floor median Offset node(s) always a part of the Metric Dimension?\n Note: 200 Random Graphs from sizes of Nodes of 3 to 22.')
    plt.ylim(0, 210)  # Set y-axis limits to 0 and 200 # IMPORTANT CHANGE THIS TO CHANGE GRAPH SCALE!!! :O
    label_list = ['Highest', 'Lowest', 'Ceil median', 'Floor median']
    plt.xticks(range(len(label_list)),  label_list)  # Set x-axis labels to seed names

    # Create bars with probability values on top
    bars = plt.bar(range(len(label_list)), probability_list, width=0.5, color=['blue', 'orange', 'green', 'red'])
    for bar, value in zip(bars, probability_list):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 3, f'{value:.2f}', ha='center')
    # plt.show()

    save_dir = "/Users/evanalba/random-geometric-graphs/images/offset/"
    plt.savefig(f"{save_dir}/{file_name}")

# get_offset_comparison(probability_list=[157.24546287256362, 189.3325593550223, 174.32054627032767, 174.0943557941372],file_name="offset_types_4_200rggs.jpg")

## Are ALL lowest offset nodes within all possible Metric Dimension R sets? ##
# # Note FIX: Different from old function because every time we first saw
# a low offset node, we just broke and went to the next r set WITHOUT considering
# there being maybe 2 or more lowest offset nodes in the same r set...
#
# PURPOSE: Calculate success of offset nodes of Five-number summary!!!
def get_offset_probability(mode, filename, datalist):
    # NOTE: If Random Graphs with RANDOM NODES AND RANDOM RADIUS CODE HERE!!!
 
    all_nodes = decode.get_items_list(file_name=f'{datalist}', nodes=True)
    all_r = decode.get_items_list(file_name=f'{datalist}', radius=True)
    all_seeds = decode.get_items_list(file_name=f'{datalist}', seed=True)
    total_rsets_r_count = 0
    total_offset_probability = 0
    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        # if (node != 20):
        #     continue
        # Round due to median being like 5.5
        round = False
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        r_sets = geo.bruteForce(G, numSets=-1)

        ## Note: Offset_dict keys are SORTED!!!
        offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
            
        ### IMPORTANT: OFFSET SETTINGS TESTING ###   
        # print(offset_dict)
        desired_offset_key = get_highest_key(offset_dict) ## CHANGE IF GETTING DIFFERENT OFFSET
        if (is_float(desired_offset_key) != False) or (desired_offset_key not in offset_dict.keys()):
            round = True
            import math
            desired_offset_key = int(math.ceil(desired_offset_key))
            # Ceil Setting ##
            if desired_offset_key not in offset_dict.keys():
                for key in offset_dict.keys():
                    if key > desired_offset_key:
                        desired_offset_key = key
                        break
            
            # Floor Setting ##
            # if desired_offset_key not in offset_dict.keys():
            #     for key in reversed(offset_dict.keys()):
            #         if key < desired_offset_key:
            #             desired_offset_key = key
            #             break

            offset_items = offset_dict[desired_offset_key]
        else:
            offset_items = offset_dict[desired_offset_key]
        # print(node, radius, seed)
        # print(offset_items)
        # print(r_sets)
        total_rsets_r_count += count_elements_in_array_of_tuples(r_sets)
        # print(total_rsets_r_count)
        # Count the number of times an offset node appears in the r_sets.
        for offset_node in offset_items:
            total_offset_probability += count_integer_in_array_of_tuples(r_sets, offset_node)
        # print(total_offset_probability)
        # break
    # return

    # IMPORTANT CHANGE FILE APPEND HERE!
    with open(f'/Users/evanalba/random-geometric-graphs/images/offset/{filename}.txt', 'a') as file:
        file.write(f'Total R sets r count: {total_rsets_r_count}') # IMPORTANT: Comment out after 1st use of same dataset!!!
        file.write(f'\n{mode}: {str(total_offset_probability)}')

get_offset_probability("Highest", filename="offset_types_2", datalist="comeback_2_1_repeat_3_to_23nodes_200graphs.list")


# def test1(mode):
#     all_nodes = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', nodes=True)
#     all_r = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', radius=True)
#     all_seeds = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', seed=True)
#     total_offset_probability = []
#     for node, radius, seed in zip(all_nodes, all_r, all_seeds):
#         G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
#         r_sets = geo.bruteForce(G, numSets=-1)
#         offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
            
#         desired_offset_key = get_lowest_key(offset_dict)
#         offset_items = offset_dict[desired_offset_key]

#         offset_found = 0
#         print(f'{offset_dict}\n{offset_items}\n{len(offset_items)}\n')
#         # print(offset_items, '\n\n', r_sets)
     
#         for lowest_offset_node in offset_items:
#             for set_ in r_sets:
#                 if lowest_offset_node in set_:
#                     print(lowest_offset_node)
#                     offset_found += 1
#                     break
#         print(f"Total Lowest nodes in R Sets: {offset_found}\n{r_sets}")        
#         break
#     #  for set_ in r_sets:
#     #         for item in offset_items:
#     #             if item in set_:
#     #                 offset_found += 1
#     #                 break
#         # total_offset_probability.append(offset_found / len(r_sets))
#     # with open('/Users/evanalba/random-geometric-graphs/images/offset/offset_types_4.txt', 'a') as file:
#     #     file.write(f'\n{mode}: {str(sum(total_offset_probability))}')

# test1("Lowest")


def test2(filename):
    all_nodes = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', nodes=True)
    all_r = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', radius=True)
    all_seeds = decode.get_items_list(file_name='comeback_4_1_repeat_3_to_23nodes_200graphs.list', seed=True)
    total_offset_probability = []

    for node, radius, seed in zip(all_nodes, all_r, all_seeds):
        G = nx.random_geometric_graph(n=node, radius=radius, seed=int(seed))
        r_sets_count = len(geo.bruteForce(G, numSets=-1))
        offset_dict = get_close_to_unique_rows_offset(analysis.get_distance_matrix(G=G, display=False))
        get_lowest_and_least_common_count(offset_dict)
        break
   

#test1(filename="comeback_2_1_repeat_3_to_23nodes_200graphs.list")
# negatives, not isolated vertices pick rate?

# Why was 0 always picked in 294604 even though the others had the same offset (some did not even appear)?


# INDIVIDUALLY for each graph go through all the offsets and calculate the probability for each one? Another experiment...