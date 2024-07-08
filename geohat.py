from collections import Counter
import analysis
import itertools
import time

# nodes = 92
# radius = 0.12999999999999998
# seed = 267868
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# analysis.get_distance_matrix(G, submatrix=False, display=False)

## Metric Dimension EXISTS
matrix = [
    [1, 2, -1, 0],
    [1, 0, 0, -1],
    [2, 8, -1, -1]
]

## Metric Dimension NOT
# matrix = [
#     [1, -1],
#     [1, -1],
#     [7, 0]
# ]

# Tests for unique column so we can find a easily a size 1 metric dimension.


def get_unique_column(matrix):
    for column in range(len(matrix[0])):
        is_unique = True
        unique = []
        for row in range(len(matrix)):
            if matrix[row][column] in unique:
                is_unique = False
                break
            unique.append(matrix[row][column])
        if is_unique:
            return column
    return False


# Gives isolated vertices so we can test for R by joining with closely to
# unique columns.
# Note: Assume Infinite Distances on Matrix are marked -1.
# Returns Isolated Vertices Columns
def get_isolated_vertices(matrix):
    isolated_vertices = []
    num_cols = len(matrix[0])
    for column in range(num_cols):
        is_isolated = True
        isolated = []
        for row in range(len(matrix)):
            double_zero = matrix[row][column] == 0 and matrix[row][column] in isolated
            non_isolated_value = matrix[row][column] != 0 and matrix[row][column] != -1
            if double_zero or non_isolated_value:
                is_isolated = False
                break
            isolated.append(matrix[row][column])
        if is_isolated:
            isolated_vertices.append(column)

    return isolated_vertices


# Get close to not having the highest count common rows' value for an
# individual column and group those columns by
# the difference in the commonality of rows they may share with other columns
# in order to combine with isolated vertices to create R.
#
# close_to_unique Dictionary Format:
# {Highest count of common value shared based on rows of an individual column of value : columns index}
# Returns Close to unique rows Columns SORTED BY KEY
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

    return dict(sorted(close_to_unique.items()))

# Give Powersets of isolated vertices so we can combine
# to look for R.
# TODO: Maybe use Powerset on close_to_unique in order to find resolving???


def powerset(iterable):
    for sl in itertools.product(*[[[], [i]] for i in iterable]):
        subset = [j for i in sl for j in i]
        yield subset

# Given some power set of isolated vertices and the power set of a
# specific key of close to unique rows columns, generate us the combination
# of these set of data.
# Returns 3rd Dimensional list.


def get_combinations(isolated_vertices, close_to_unique):

    isolated_combo = list(powerset(isolated_vertices))
    column_type_combo = list(powerset(close_to_unique))

    return list(itertools.product(isolated_combo, column_type_combo))


def is_resolving_set(distance_matrix, test_set):
    seen_rows = set()

    for row in distance_matrix:
        row_tuple = tuple([row[i] for i in test_set])
        if row_tuple in seen_rows:
            return False
        seen_rows.add(row_tuple)

    return True


def get_r_isolated_and_close_to_unique(distance_matrix, third_matrix):
    sorted_list = sorted(third_matrix, key=lambda layer: len(layer))

    for layer in sorted_list:
        close_to_unique_exists = len(layer[1]) > 1
        both_isolated_and_close_to_unique = (len(layer[0]) > 0 and
                                             len(layer[1]) > 0)
        if close_to_unique_exists or both_isolated_and_close_to_unique:
            test_set = set(layer[0] + layer[1])
            # Maybe make an array to check if in array prevent duplicates
            # being runned agained in the is_resolving_set function???
            # Will that make a time difference?
            # print(test_set)

            result = is_resolving_set(distance_matrix, test_set)
            if result == True:
                return test_set
    return False


# Generate occurences least common elements sorted in order for the 2nd
# approach.
# Dictionary Format: 
# { Count of Occurence : [ [ Elements ], [Column(s) of 0th index Element], [Column(s) of 1th index Element] }
# 0th index of list item is always the elements.s
def get_least_common_elements(distance_matrix):
    element_counts = Counter(sum(distance_matrix, []))
    least_common_elements = {}
    # print(element_counts,'\n')
    for element, count in element_counts.items():
        if count not in least_common_elements:
            # New Count of Occurence
            least_common_elements[count] = [[]]
        # [ Element ]
        least_common_elements[count][0].append(element)

        # [Column(s) of Element], [Column(s) of Element]
        # Find All Columns for each element
        element_column_indices = set()
        for i in range(len(distance_matrix)):
            for j in range(len(distance_matrix[i])):
                if distance_matrix[i][j] == element:
                    element_column_indices.add(j)
        least_common_elements[count].append(list(element_column_indices))
  
    return dict(sorted(least_common_elements.items()))

# Helper function to primarily FIND and get more least columns as I go, 
# increases R size.
# Combined with is_resolving_set() to find R.
def get_columns_with_unique_elements(matrix, least_common):
    unique_column_set = set()

    for key, value in least_common.items():
        # value[0] <-- First List of Elements
        for inner_list in value[1:]:
            for column in inner_list:
                unique_column_set.add(column)
    if len(unique_column_set) == 0:
        return False
    return unique_column_set

                
def iterate_increasing_slice(data_list, start_index=0):
    slice_size = 2
    while slice_size <= len(data_list):
        yield data_list[start_index: slice_size]
        slice_size += 1

# 2nd Approach
def get_r_based_on_least_occurences(distance_matrix, least_common):
    unique_column_set = list(get_columns_with_unique_elements(distance_matrix, least_common))
    # unique_column_set = [1, 2, 3, 4, 5, 6]
    test_sets = iterate_increasing_slice(data_list=unique_column_set)
    for columns in test_sets:
        is_r_set = is_resolving_set(distance_matrix, columns)
        if is_r_set == True:
            return columns
    return False


def geohat(distance_matrix, option=[1]):
    if 1 in option:
        # Size 1 Metric Dimension
        if get_unique_column(distance_matrix) != False:
            return get_unique_column(distance_matrix)

        ### Approaches for Metric Dimension ###
        # Maybe 1 approach is faster and more accurate???

    if 2 in option:
        # 1st Approach: Check for close to unique row column and use if possible
        # isolated vertices.
        isolated_vertices = get_isolated_vertices(distance_matrix)
        close_to_unique = get_close_to_unique_columns(distance_matrix)

        # Loop through all of close_to_unique a good idea in terms of time???
        for key in close_to_unique:
            combinations = get_combinations(
                isolated_vertices, close_to_unique[key])
            is_r_set = get_r_isolated_and_close_to_unique(
                distance_matrix, combinations)
            if is_r_set != False:
                return list(is_r_set)
        # Converting to list affects time significantly??

    if 3 in option:
        # 2nd Approach: Use the matrix to pick columns based on the least common
        # elements gathered in the whole matrix.
        least_common = get_least_common_elements(distance_matrix)
        is_r_set = get_r_based_on_least_occurences(distance_matrix, least_common)
        if is_r_set != False:
            return is_r_set

    if 4 in option:
        # Approaches 1st + 2nd = 3rd
        print('')
    
    if 5 in option:
        # Approaches 1st (Uses ISOLATED VERTICES ONLY) + 3rd
        print('')
    
    if 6 in option:
        # Approaches 1st (Uses CLOSE ROW COLUMNS ONLY) + 3rd
        print('')

    return False



# start = time.perf_counter()
#             resSet = geo.ich(G)
#             end = time.perf_counter()
#             execution_time = (end - start)

# Returns Time and Resolving Set
def get_stats_geohat(matrix, repeat = 100, option=[]):

    start = time.perf_counter()
    r_set = geohat(matrix, option=option)
    end = time.perf_counter()
    execution_time = (end - start)
    return r_set, execution_time

# r_set, execution_time = get_stats_geohat(matrix, repeat=1, option=[1])
# print(f'R Set: {r_set} \nExecution Time: {execution_time} \n')



# repeat = 100

# start = time.perf_counter()
# print(geohat(matrix, option=[2]))
# end = time.perf_counter()
# execution_time = (end - start)
