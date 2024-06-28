import decode
import analysis
import matplotlib.pyplot as plt
import multilateration as geo
import networkx as nx
import os

# Find the unique R
# nodes = 34
# radius = 0.2
# seed_list = [852397, 763785, 726260, 657341, 628768, 614008, 439468, 437162, 289604, 267652]

# for seed in seed_list:
#     G = nx.random_geometric_graph(n=nodes, radius=radius, seed=seed)
#     analysis.get_unique_resolve_runs(filename=seed, nodes=nodes, radius=radius, seed=seed, G=G)

# from itertools import chain, combinations, product
# import timeit

# def mpowerset(iterable):
#     "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
#     s = list(iterable)
#     return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# def ppowerset(iterable):
#     for sl in product(*[[[], [i]] for i in l]):
#         yield {j for i in sl for j in i}

# def try_powerset(f):
#     def rf():
#         f(range(16))
#     t = timeit.Timer(stmt=rf)
#     try:
#         r = t.repeat(10)
#         print(r, min(r))
#     except Exception:
#         t.print_exc()

# def main():

#     # print("MPOWERSET: ", '\n') 
#     # try_powerset(mpowerset)

#     print("PPOWERSET: ", '\n') 
#     try_powerset(ppowerset)

# if __name__ == "__main__":
#     main()

# from itertools import product


# def powerset(iterable):
#   """
#   Finds the power set of an iterable object, represented as lists.

#   Args:
#       iterable: An iterable object (e.g., list, tuple).

#   Yields:
#       list: A list representing a subset of the original iterable.
#   """

#   for sl in product(*[[[], [i]] for i in iterable]):
#     subset = [j for i in sl for j in i]
#     yield subset


# # Example usage
# l = ["A", "B", "C"]

# # for subset in powerset(l):
# #   print(subset)
# print(list(powerset(l)))

# print("Done printing power set elements.")

my_3d_list = [[[1, 2], [3, 4]], [[5, 6]], [[7, 8, 9]]]

# Sort by layer length (ascending) using key function
sorted_list = sorted(my_3d_list, key=lambda layer: len(layer))

print("Original list:")
print(my_3d_list)

print("\nSorted list by layer length (ascending):")
print(sorted_list)

