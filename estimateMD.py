#Author: Matthew J. Hernandez
#Updated: 2024-07-11
#This is based off of the data collected by Dr. Richard Carter Tillquist

#Update this file to include number of components/iso given n and r for below the threshold

n = 0 #number of nodes
r = 0.0 #size of radius

#dict in Python
#radii on y-axis
#nodes on x-axis
metricDimensionData = { 'Nodes': {'n': 500, 'r': 19}, 'Radii': {'name': 'Bob', 'age': 25}} #nested dictionary
#key is name of bucket
#value is what we are storing

#if below, then use one function:

#possibly neural networks, decision trees, random forrests, etc
#or we can use a linear regression to be more explicit
#use curve fitting for linear regression

#if above, then use another function:

#Find logistic curve
#or find cubic fit, but we will need to generalize the curve

#This function estimates and prints the Metric Dimension of a graph given the number of nodes and the desired radius
def estimateMD(n, r):
    if (n==0):
       metricDimension = 0
    return metricDimension

n = int(input("What is the number of nodes for your graph?\n"))

r = float(input("What is the given radius?\n"))

print("The estimated Metric Dimension for your graph with ", n, " nodes and a radius of ", r, " is: ", estimateMD(n, r) )
