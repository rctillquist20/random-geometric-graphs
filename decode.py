from experiments import readList
import os.path


file_name = 'rgg_data.list'

# Returns data that can be filter based on what what we collected so can
# analyze it.
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

        for item in filtered_data:
            print('\n')
            print('Nodes: ', item[0])
            print('Radius: ', item[1])
            print('Seed: ', item[2])
            print('Resolving Set: ', item[3])
            print('Execution Time: ', item[4])
        print('\n')

        # Note: Returns R Set always to it be used in combination
        # with analysis.py to draw R set on Matplotlib Graph.
        return item[3]
    except:
        print('Error: Can not decode and read file.')
        return None

# get_data(sort_by=0, ascending=False)
