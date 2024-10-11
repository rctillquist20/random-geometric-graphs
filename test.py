# TEST HERE

import decode

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
# Example usage:
matrix = [
[0, 1, 2, 1, 2, 3],
[1, 0, 1, 1, 1, 2],
[2, 1, 0, 2, 2, 1],
[1, 1, 2, 0, 2, 3],
[2, 1, 2, 2, 0, 3],
[3, 2, 1, 3, 3, 0]
]

# result = count_elements_and_group(matrix)
result = get_close_to_unique_rows_offset(matrix)
print(result)