from experiments import readList
import os.path

file_name = 'rgg_data.list'

if not os.path.isfile(file_name):
    print('Error: File does not exist.')
else:
    try:
        data_list = readList(file_name)
        for item in data_list:
            print('\n')
            print(item)
        print('\n')
    except:
        print('Error: Can not decode and read file.')
