#Author: Matthew J. Hernandez and Dr. Richard Carter Tillquist
#Updated: 2024-07-16
#This is based off of the data collected by Dr. Richard Carter Tillquist

n = 0 #number of nodes
r = 0.0 #size of radius

metricDimensionData = { 'Nodes': {'500': 500, 'r': 19}, 'Radii': {'sample': 0.0, 'age': 25}} #nested dictionary
#key is name of bucket
#value is what we are storing

#if below, then use one function:

#possibly neural networks, decision trees, random forrests, etc
#or we can use a linear regression to be more explicit
#use curve fitting for linear regression

#if above, then use another function:

#Find logistic curve
#or find cubic fit, but we will need to generalize the curve

#This function predicts the Metric Dimension of a graph given the number of nodes and the desired radius
def predictMD(n, r):
    #below threshold estimate function
    #above threshold estimate function
    #below threshold for actual data
    #above threshold for actual data
    info = {}
    for (n,r,seed,resSet,t) in data:
        if r <= np.sqrt(np.log(n)/(np.pi*n)):
            info[(n,r)] = info.get((n,r), []) + [len(resSet)]
    
    if (data):
        return metricDimensionPrediction
    elif(noData and belowThreshold):
        return linearRegression
    else:
        return neuralNetwork

for n in [n for (n,_) in info.keys()]:
  X, Y = zip(*[(r, val) for (m,r) in info for val in info[(m,r)] if m==n])
  X = [[x] for x in X]
  model = LinearRegression().fit(X, Y)
  print(n, 'model info', model.coef_, model.intercept_, model.score(X, Y)) 

def numComponents(G):
  return len(list(nx.connected_components(G)))

def numIso(G):
  return len([c for c in nx.connected_components(G) if len(c)==1])

n = int(input("What is the number of nodes for your graph?\n"))

r = float(input("What is the given radius?\n"))

print("The estimated Metric Dimension for your graph with ", n, " nodes and a radius of ", r, " is: ", predictMD(n, r))