# Calculates in the special case get_threshold of a two-dimensional space and
# the euclidean norm (d = 2 and p = 2) this yields r ~ sqrt( ln(n) / (pi * n) )
# for random geometric graphs.
# Note: Specifically for below that threshold.

import math
import numpy as np


# Returns the connectivity value that yields r ~ sqrt( ln(n) / (pi * n) ) to
# help us compare if we are ubove or below the connectivity threshold.


def get_threshold(n):
    return math.sqrt(math.log(n) / (math.pi * n))

# Returns all the n values that have a threshold BELOW some given radius.
# r = 0.3
# [1, 10, 40, 10, 20]
def get_n_below_radius(starting_n, radius, repeat=1):
    n_sizes = {}
    while repeat != 0:
        threshold = get_threshold(starting_n)
        if (radius > threshold):
            n_sizes.update({starting_n: threshold})
            repeat -= 1
        starting_n += 1
    return n_sizes


# Returns the what Radii given in a list is in order to distinguish what
# below the connectivity threshold for random geometric graphs.

# Future Thought: Provide an n list below threshold in respect to r???
def get_radius_below_on_n(n, radius_list=[]):
    below_threshold = [r for r in radius_list if r < get_threshold(n)]
    return below_threshold

# print(get_radius_based_on_n(100, [0.1, 0.2, 0.3]))


# print(get_n_below_radius(starting_n=1, radius=0.14, repeat=10))

rList = list(np.arange(0.02, 0.14, 0.01)) + \
    list(np.arange(0.2, np.sqrt(2)+0.1, 0.1))

# Show repeat 10 (pick item 10 in list) works!
for x in rList:
    print(x)
    print('\n')
    print(get_n_below_radius(starting_n=1, radius=x, repeat=10))
    print('\n')

print('Total unique radii:', len(rList))
