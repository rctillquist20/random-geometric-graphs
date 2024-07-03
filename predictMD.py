#Author: Matthew J. Hernandez
#Updated: 2024-07-03
#This is based off of the data collected by Dr. Richard Carter Tillquist

n = 0
r = 0.0

#This function estimates and prints the Metric Dimension of a graph given the number of nodes and the desired radius
def estimatedMD(n, r):
    if (n >= 0 & n <= 1):
        metricDimension = 0
    print("The estimated Metric Dimension for your graph with " + n + " nodes and a radius of " + r + " is: " )
    



n = input("What is the number of nodes for your graph?\n")
r = input("What is the given radius?\n")
estimatedMD(n, r)
