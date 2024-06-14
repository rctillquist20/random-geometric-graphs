# Calculates in the special case threshold of a two-dimensional space and 
# the euclidean norm (d = 2 and p = 2) this yields r ~ sqrt( ln(n) / (pi * n) ) 
# for random geometric graphs.
# Note: Specifically for below that threshold.

import math

n = 1
radius = 0.3
repeat = 5

n_sizes = {}

while repeat != 0:
    threshold = math.sqrt((math.log(n) / (math.pi * n)))
    if (radius > threshold):
        n_sizes.update({n : threshold})
        repeat -= 1
    n += 1

print(n_sizes)
