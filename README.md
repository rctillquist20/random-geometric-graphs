# Random geometric graphs

<img src="https://github.com/rctillquist20/random-geometric-graphs/blob/evanalba/images/metric_dimension_logo.png?raw=true" width="250px" height="150px">

Given a graph G, a subset of vertices R is called a resolving set when, for all distinct pairs of vertices u and v, there is at least one r ∈ R such that d(r,u) ≠ d(r,v) where d(x,y) is the shortest path distance between vertices x and y. The metric dimension of G is the size of smallest resolving sets on the graph. This concept is closely related to ideas underlying GPS or the Global Positioning System and has applications in robot navigation, source localization, and representing genetic sequences among others. Determining the exact metric dimension of an arbitrary graph is an NP-hard problem. While significant work has been done regarding the metric dimension of specific families of graphs, relatively little is known about the behavior of metric dimension in the context of random graph models. In this work we will investigate a characterization of the metric dimension of certain classes of random geometric graphs. We hope to identify patterns relating metric dimension to parameters of these models which may serve as the basis of asymptotic bounds and fast heuristic algorithms.

## Datasets
`rgg_data.list` - Dr. Tillquist's Data\
`rgg_data_10.list` - 10 repeats of RGGs (Note: A good portion of them are 10 node graphs.)\
`rgg_data_10.geohat or ich or random` - 10 repeats of RGGs of the same rgg_data_10.list parameters but using these algorithms to gather metric dimension and time execution.\
`comeback_1_10.list` - RGGs from 3-23 nodes with random radiuses. **Each N family of graphs share the same radius.**\
`comeback_2_1_repeat_3_to_23nodes_200graphs` - RGGs from 3-23 nodes with random radiuses.