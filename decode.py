from experiments import readList
import os.path

file_name = 'rgg_data.list'


# Returns data that can be filter based on what what we collected so can
# analyze it.
def get_data(nodes=None, radius=None, seed=None, r_set=None,
             execution_time=None):
    if not os.path.isfile(file_name):
        print('Error: File does not exist.')
    else:
        try:
            data_list = readList(file_name)

            filtered_data = [item for item in data_list if
                             (nodes is None or item[0] == nodes) and
                             (radius is None or item[1] == radius) and
                             (seed is None or item[2] == seed) and
                             (r_set is None or item[3] == r_set) and
                             (execution_time is None or
                              item[4] == execution_time)]

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


# get_data(nodes=2,seed=854900)
