# TEST HERE

# pickle = [['q', 'p'], ['j', 'q']]
# if ['q', 'p'] or  ['p', 'q'] in pickle:
#    print('TRUE!!')

#import decode

# test = decode.get_data(file_name='comeback_2_1_repeat_3_to_23nodes_200graphs.list', output=False)
# for i in test:
#   print("\nYOLO:\n", i)

#print(decode.get_items_list(file_name='comeback_3_1_repeat_3_to_23nodes_200graphs.list'))

# def count_elements_and_group(matrix):
#     """Counts the elements in a matrix and groups them by their count.

#     Args:
#         matrix: A 2D list or array of integers.

#     Returns:
#         A dictionary where keys are the count of elements and values are lists of elements with that count.
#     """

#     counts = {}
#     for row in matrix:
#         seen = set()
#         for element in row:
#             if isinstance(element, int):
#                 if element not in seen:
#                     count = counts.get(element, 0) + 1
#                     counts[count] = counts.setdefault(count, []) + [element]
#                     seen.add(element)
#     return counts

# Finds the element with the highest count in a specific matrix row array so 
# can get the highest offset.
### IMPORTANT -> Offset 1: All Unique rows.

def get_element_with_highest_count(array):
    count_dict = {}
    print(array)
    for element in array:
        # print(element)
        count_dict[element] = count_dict.get(element, 0) + 1
    max_count = max(count_dict.values())

    return max_count

def get_close_to_unique_rows_offset(matrix):
    offset = {}

    for row_index, row in enumerate(matrix):
        offset.setdefault(get_element_with_highest_count(row), []).append(row_index)

    return dict(sorted(offset.items()))


# Helps us get the lowest offset dictionary key.
def get_lowest_key(dictionary):
    if not dictionary:
        return None

    min_key = min(dictionary, key=dictionary.get)
    return min_key


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

import statistics
# Example usage:
matrix = [
[0, 0, 0, 0, 0, 0], # Row 0
[1, 0, 1, 1, 1, 2], 
[2, 1, 0, 2, 2, 1],
[0, 1, 2, 3, 4, 5],
[4, 1, 2, 2, 0, 3],
[1, 1, 1, 1, 1, 1]  # Row 5
]
# All we care about is rows really.

# result = count_elements_and_group(matrix)
print(matrix)
print()
print()

offset_dict = get_close_to_unique_rows_offset(matrix)
print(offset_dict)



# # print(result)
# key = get_lowest_key(offset_dict)
# print(f'Lowest:\n{key}')
# print(f'{offset_dict[key]}')

# key2 = get_lower_quartile_key(offset_dict, method='Exclusive')
# print(f'Ceil Exclusive Lower Quartile:\n{key2}')
# print(f'{offset_dict[key2]}')


# time_diff = [i for i in range(1, 11)]
# # Example source: https://www.scribbr.com/statistics/quartiles-quantiles/
# # time_diff = [2, 2, 4, 5, 5, 5, 8, 9, 9, 9, 12]
# print(time_diff,'\nExclusive:\n')
# # Split:
# # Quartiles (4-quantiles): Three quartiles (points of data) split the data into four parts.
# # Cats and whiskers.
# # Deciles (10-quantiles): Nine deciles split the data into 10 parts.

# print(statistics.quantiles(data=time_diff, n=4, method='exclusive'))
# print("Inclusive:\n",statistics.quantiles(data=time_diff, n=4, method='inclusive'))

# def count_elements_in_array_of_tuples(array):
#   count = 0
#   for tuple in array:
#     count += len(tuple)
#   return count

# Example usage:
# my_array = [(1, 2, 3), (4, 5), (6, 7, 8, 9)]
# print(count_elements_in_array_of_tuples(my_array))  # Output: 9
# print(len([(1, 3), (4, 5, 1)]))

# def count_integer_in_array_of_tuples(array, target_integer):
#   count = 0
#   for tuple in array:
#     count += tuple.count(target_integer)
#   return count

# # Example usage:
# my_array = [(1, 2, 3), (1, 1, 1), (6, 7, 8, 1)]
# target_integer = 1
# occurrences = count_integer_in_array_of_tuples(my_array, target_integer)
# # print(occurrences)  # Output: 5

# import statistics

# def get_upper_quartile_key(dictionary, method):
#   if (method == "exclusive") or (method == "inclusive"):
#     values = list(dictionary.keys())
#     if len(values) > 1:
#         upper_quartile = 2
#         return statistics.quantiles(values, n=4, method=f"{method}")[upper_quartile]
#     return values[0]
 
#   print("Error: Quantile method not exclusive or inclusive.")
#   quit()



# import random


# # Create a sample dictionary with random values
# sample_dict = {1:[0, 3]}
# print(sample_dict[-1])
# # Get the lower quartile key
# lower_quartile_key = get_upper_quartile_key(sample_dict, method="exclusive")

# # Print the result
# print("Lower quartile key:", lower_quartile_key)
