from experiments import readList
import os.path


file_name = 'rgg_data.list'

# Returns data that can be filter based on what what we collected so can
# analyze it.
# Parameters:
# - nodes
# - radius
# - seed
# - r_set (Resolving Set)
# - execution time (Time in seconds)
# - sort_by
# - ascending (data) Default: True
# - output (Displays information about data on file.) Default: True


def get_data(nodes=None, radius=None, seed=None, r_set=None,
             execution_time=None, sort_by=None, ascending=True):

    if not os.path.isfile(file_name):
        print('Error: File does not exist.')
        return None

    try:
        data_list = readList(file_name)

        filtered_data = [item for item in data_list if
                         (nodes is None or item[0] == nodes) and
                         (radius is None or item[1] == radius) and
                         (seed is None or item[2] == seed) and
                         (r_set is None or item[3] == r_set) and
                         (execution_time is None or item[4] == execution_time)]

        if sort_by is not None:
            def sort_by_item(item):
                return item[sort_by]
            filtered_data.sort(key=sort_by_item, reverse=not ascending)

        # if output == False:
        #     return filtered_data
        # else:
        for item in filtered_data:
            print('\n')
            print('Nodes: ', item[0])
            print('Radius: ', item[1])
            print('Seed: ', item[2])
            print('Resolving Set: ', item[3])
            print('Execution Time: ', item[4])
            print('\nPositions: ', item[5])
        print('\n')
        return item
    except:
        print('Error: Can not decode and read file.')
        return None


nodes = 3
radius = 1
seed = 7637

# get_data(nodes=nodes, radius=radius, seed=seed, output=False)
