import decode
import analysis
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

# Find the unique R
# nodes = 34
# radius = 0.2
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)

# create a dictionary with keys and values
# from collections import defaultdict

# countries = {1: [3, 4], [[0,1], [9, 10]], 22: 9, 5: 3}
# Dictionary Format:
# { Count of Occurence : [ [ column], [ [Column(s) of Element], [Column(s) of Element] ] }
# countries = {1: [[8], [1]], 2: [[1, 2], [0], [0, 1]], 3: [[0], [1, 2, 3]], 4: [[-1], [2, 3]]}

# Add Element
# countries[1][0].append(9)
# Add Column List Item
# countries[1][1][0].append(7)
# Add Column List
# countries[1][1].append([])
# print(countries)
# Add Key
# countries[2] = [[], [[]]]
# print(countries)

# countries[5] = 69
# for index, item in enumerate(countries):
#     print(index)
# i = 0
# for key, item in countries.items():
#     print(i)
#     i += 1
# my_list = {1: [[8], [1]], 2: [[1, 2], [0], [0, 1]], 3: [[0], [1, 2, 3]], 4: [[-1], [2, 3]]}

# for key, value in my_list.items():
#   # value[0] <-- First List of Elements
#   for inner_list in value[1:]:
#     for column in inner_list:
#       print(f"Key: {key}, Column: {column}")
def iterate_increasing_slice(data_list, start_index=0):
    slice_size = 1
    while slice_size <= len(data_list):
        yield data_list[start_index: slice_size]
        slice_size += 1

# Example usage
data_list = [1, 2, 3, 4, 5, 6]

for slice in iterate_increasing_slice(data_list):
    print(slice)




def draw_graph(G, static_pos=None, show_resolving=True, r_set=[]):
    try:
        if show_resolving == True:
            color_map = []
            for node in G:
                if node in r_set:
                    color_map.append('red')
                else:
                    color_map.append('cyan')
            nx.draw(G, pos=static_pos, with_labels=True, font_weight='bold',
                    node_color=color_map, edge_color='black')
        else:
            nx.draw(G, with_labels=True, font_weight='bold',
                    node_color='cyan', edge_color='black')
        plt.show()
    except:
        print('Error: Specific graph cannot be drawn.')

# nodes = 32
# radius = 0.2
# seed = 852397
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)

# draw_graph(G,
#            static_pos=decode.get_data(
#                nodes=nodes, radius=radius, seed=seed, output=False)[5],
#            r_set=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False)[3])

# draw_graph(G, static_pos=decode.get_data(nodes=nodes, radius=radius, seed=seed, output=False))

# def find_unique_numbers(filename):
#     """
#     Finds and prints all unique numbers from a text file line by line.

#     Args:
#         filename: The path to the text file.
#     """

#     unique_numbers = set()
#     try:
#         with open(filename, 'r') as file:
#             for line in file:
#                 # Remove leading/trailing whitespace and split into words
#                 words = line.strip().split()
#                 for word in words:
#                     # Try converting to integer
#                     try:
#                         number = int(word)
#                         unique_numbers.add(number)
#                     except ValueError:
#                         # Ignore non-numeric elements
#                         pass
#     except FileNotFoundError:
#         print(f"Error: File '{filename}' not found.")

#     if unique_numbers:
#         print("Unique numbers found:")
#         for number in unique_numbers:
#             print(number)
#     else:
#         print("No unique numbers found in the file.")

# def find_unique_numbers(filename):
#   """
#   Finds and prints all unique numbers from a text file, handling lines containing
#   number tuples and skipping the first line.

#   Args:
#       filename: The path to the text file.
#   """

#   unique_numbers = set()
#   try:
#     with open(filename, 'r') as file:
#       # Skip the first line
#       next(file)

#       for line in file:
#         # Remove leading/trailing whitespace
#         line = line.strip()

#         # Check if line is empty (skip empty lines)
#         if not line:
#             continue

#         try:
#           # Assuming tuples are enclosed in parentheses
#           numbers = eval(line)  # Evaluate the line as a Python expression
#           # Extract individual numbers from the tuple
#           unique_numbers.update(numbers)
#         except (SyntaxError, ValueError) as e:
#           print(f"Error: Line in file '{filename}' is invalid: {e}")

#   except FileNotFoundError:
#     print(f"Error: File '{filename}' not found.")

#   if unique_numbers:
#     print("Unique numbers found:\n")
#     print(sorted(unique_numbers))
#   else:
#     print("No unique numbers found in the file.")


# # Example Usage
# filename = "metric_d/d_10/34/852397.txt"
# find_unique_numbers(filename)
