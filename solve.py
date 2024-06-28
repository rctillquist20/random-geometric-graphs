import analysis
import itertools

# 1. Check for unique column
# 
# 3.

# nodes = 92
# radius = 0.12999999999999998
# seed = 267868
# G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
# analysis.get_distance_matrix(G, submatrix=False, display=False)

matrix = [
    [1, 2, -1, 0],
    [1, 0, 0, -1],
    [7, 8, -1, -1]
]

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
        row_tuple = tuple(row)
        if row_tuple in seen_rows:
            return False
        seen_rows.add(row_tuple)

    return True


def get_r_isolated_and_close_to_unique(distance_matrix, third_matrix):
    sorted_list = sorted(third_matrix, key=lambda layer: len(layer))

    for layer in sorted_list:
        close_to_unique_exists = len(layer[1]) > 1
        both_isolated_and_close_to_unique = (len(layer[0]) > 0  and \
                                             len(layer[1]) > 0)
        if close_to_unique_exists or both_isolated_and_close_to_unique:
            test_set = set(layer[0] + layer[1])
            # Maybe make an array to check if in array prevent duplicates 
            # being runned agained in the is_resolving_set function???
            # Will that make a time difference?

            result = is_resolving_set(distance_matrix, test_set)
            if result == True:
                return test_set
    return False


def geohat(distance_matrix):
    # Size 1 Metric Dimension
    if get_unique_column(distance_matrix) != False:
        return get_unique_column(distance_matrix)
    
    ### 2 Approaches for Metric Dimension ###
    
    # 1st Approach: Check for close to unique row column and use if possible 
    # isolated vertices.
    isolated_vertices = get_isolated_vertices(distance_matrix)
    close_to_unique = get_close_to_unique_columns(distance_matrix)

    # Loop through all of close_to_unique a good idea in terms of time??? 
    for key in close_to_unique:
        combinations = get_combinations(isolated_vertices, close_to_unique[key])
        is_r_set = get_r_isolated_and_close_to_unique(distance_matrix, combinations)
        if is_r_set != False:
            return is_r_set
    
    # 2nd Approach: Use the matrix to pick columns based on the least common 
    # elements gathered in the whole matrix.

print(geohat(matrix))
