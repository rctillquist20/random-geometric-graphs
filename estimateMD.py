#Author: Matthew J. Hernandez
#Updated: 2024-07-05
#This is based off of the data collected by Dr. Richard Carter Tillquist

n = 0 #number of nodes
r = 0.0 #size of radius

x = {"name" : "John", "age" : 36} #Sample dict in Python

#This function estimates and prints the Metric Dimension of a graph given the number of nodes and the desired radius
def estimateMD(n, r):
    if (n >= 0 & n <= 1):
        metricDimension = 0
    print("The estimated Metric Dimension for your graph with " + n + " nodes and a radius of " + r + " is: " )
    
#2d array or matrix
#nodes on top
#radii on left

#look at Evan's getDistanceMatrix file in his branch
#can filter columns

#Carter suggests dictionary of dictionary instead of lists of lists, refer to Python documentation
#dicts are like hash tables
#lists don't quite match up

n = input("What is the number of nodes for your graph?\n")
r = input("What is the given radius?\n")
print("The estimated Metric Dimension for your graph with " + n + " nodes and a radius of " + r + " is: " + estimateMD(n, r) )


