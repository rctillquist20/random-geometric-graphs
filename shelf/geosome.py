import sys
sys.path.insert(1, '/Users/evanalba/random-geometric-graphs/')
import geohat

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

print(geohat.get_isolated_vertices(matrix))