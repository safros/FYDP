import sys
#import gurobipy as gp
#from gurobipy import GRB
#import math
from itertools import combinations

class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)

    def construct_graph(self, nodes, init_graph):
        '''
        This method makes sure that the graph is symmetrical. In other words, if there's a path from node A to B with a value V, there needs to be a path from node B to node A with a value V.
        '''
        graph = {}
        for node in nodes:
            graph[node] = {}

        graph.update(init_graph)

        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value

        return graph

    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.nodes

    def get_outgoing_edges(self, node):
        "Returns the neighbors of a node."
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections

    def value(self, node1, node2):
        "Returns the value of an edge between two nodes."
        return self.graph[node1][node2]


def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())

    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph
    shortest_path = {}

    # We'll use this dict to save the shortest known path to a node found so far
    previous_nodes = {}

    # We'll use max_value to initialize the "infinity" value of the unvisited nodes
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    # However, we initialize the starting node's value with 0
    shortest_path[start_node] = 0

    # The algorithm executes until we visit all nodes
    while unvisited_nodes:
        # The code block below finds the node with the lowest score
        current_min_node = None
        for node in unvisited_nodes:  # Iterate over the nodes
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        # The code block below retrieves the current node's neighbors and updates their distances
        neighbors = graph.get_outgoing_edges(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)

    return previous_nodes, shortest_path


def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node

    while node != start_node:
        path.append(node)
        node = previous_nodes[node]

    # Add the start node manually
    path.append(start_node)

    print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
    print(" -> ".join(reversed(path)))
    return reversed(path)

#declare graph
# nodes = ["R", "O", "M", "L", "RO", "B", "BE", "A"]
#
# init_graph = {}
# for node in nodes:
#     init_graph[node] = {}
#
# init_graph["R"]["O"] = 5
# init_graph["R"]["M"] = 7
# init_graph["R"]["L"] = 4
# init_graph["R"]["RO"] = 900000
# init_graph["R"]["B"] = 900000
# init_graph["R"]["A"] = 900000
# init_graph["R"]["RO"] = 900000
# init_graph["R"]["R"] = 10000000000
# init_graph["O"]["B"] = 1
# init_graph["O"]["M"] = 3
# init_graph["O"]["R"] = 10
# init_graph["O"]["L"] = 30
# init_graph["O"]["RO"] = 12
# init_graph["O"]["BE"] = 300
# init_graph["O"]["A"] = 24
# init_graph["M"]["BE"] = 5
# init_graph["M"]["A"] = 4
# init_graph["A"]["BE"] = 1
# init_graph["RO"]["B"] = 2
# init_graph["RO"]["A"] = 2
# init_graph["RO"]["R"] = 20
# init_graph["RO"]["O"] = 12
# init_graph["RO"]["M"] = 2
# init_graph["RO"]["L"] = 2
# init_graph["RO"]["BE"] = 20
# init_graph["BE"]["R"] = 5
# init_graph["BE"]["O"] = 5000
# init_graph["BE"]["M"] = 50
# init_graph["BE"]["L"] = 500
# init_graph["BE"]["RO"] = 5
# init_graph["BE"]["B"] = 3
# init_graph["BE"]["A"] = 5
# init_graph["L"]["R"] = 5
# init_graph["L"]["O"] = 3
# init_graph["L"]["M"] = 7
# init_graph["L"]["RO"] = 3
# init_graph["L"]["B"] = 7
# init_graph["L"]["BE"] = 8
# init_graph["L"]["A"] = 18
# init_graph["B"]["R"] = 5
# init_graph["B"]["O"] = 3
# init_graph["B"]["M"] = 7
# init_graph["B"]["L"] = 8
# init_graph["B"]["RO"] = 3
# init_graph["B"]["BE"] = 8
# init_graph["B"]["A"] = 18
# graph = Graph(nodes, init_graph)
# previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node="R")
# print_result(previous_nodes, shortest_path, start_node="R", target_node="BE")
# print_result(previous_nodes, shortest_path, start_node="R", target_node="L")

#code adapted from https://gurobi.github.io/modeling-examples/traveling_salesman/tsp.html
#declare variables
#-CLC: 1105 Fountain St N, Cambridge, ON N3E 1A2
#-address of grocery stores:
#1.875 Highland Rd W, Kitchener, ON N2N 2Y2 (Superstore)
#2.50 Westmount Rd N Unit B1, Waterloo, ON N2L 6N9 (T&T)
#3.750 Ottawa St S, Kitchener, ON N2E 1B6 (Zehrs)
# ESAL_ijk = [[]]
# GHG_ijk = [[]]
# demand_Retailer = []
# capacity_tuck= []
# y_ik = [0, 1,1,1]
# CLCto_retailers=[1, 2, 3,4]
# adjacencyMatrix = [[100000000, 16.3, 24.1, 14],
#                        [16.3, 1000000000, 5.4, 5.2],
#                        [24.1, 5.4, 100000000, 7.8],
#                        [14, 5.2, 7.8, 1000000000]]
#
# def distance(city1, city2):
#     #c1 = coordinates[city1]
#     #c2 = coordinates[city2]
#     #diff = (c1[0]-c2[0], c1[1]-c2[1])
#     #return math.sqrt(diff[0]*diff[0]+diff[1]*diff[1])
#     return adjacencyMatrix [city1][city2]
#
# # Callback - use lazy constraints to eliminate sub-tours
# def subtourelim(model, where):
#     if where == GRB.Callback.MIPSOL:
#         # make a list of edges selected in the solution
#         vals = model.cbGetSolution(model._vars)
#         selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
#                              if vals[i, j] > 0.5)
#         # find the shortest cycle in the selected edge list
#         tour = subtour(selected)
#         if len(tour) < len(CLCto_retailers):
#             # add subtour elimination constr. for every pair of cities in subtour
#             model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
#                          <= len(tour)-1)
#
# # Given a tuplelist of edges, find the shortest subtour
# def subtour(edges):
#     unvisited = CLCto_retailers[:]
#     cycle = CLCto_retailers[:] # Dummy - guaranteed to be replaced
#     while unvisited:  # true if list is non-empty
#         thiscycle = []
#         neighbors = unvisited
#         while neighbors:
#             current = neighbors[0]
#             thiscycle.append(current)
#             unvisited.remove(current)
#             neighbors = [j for i, j in edges.select(current, '*')
#                          if j in unvisited]
#         if len(thiscycle) <= len(cycle):
#             cycle = thiscycle # New shortest subtour
#     return cycle
#
# # tested with Python 3.7 & Gurobi 9.0.0
# m = gp.Model()
#
# # Variables: is city 'i' adjacent to city 'j' on the tour?
# x_ij = m.addVars(CLCto_retailers, obj=0.05, vtype=GRB.BINARY, name='x')
#
#
# # Constraints: two edges incident to each city
# #cons = m.addConstrs(vars.sum(c, '*') == 2 for c in capitals)
# trucksNum = range(len(y_ik))
# numPoints = range(len(CLCto_retailers))
# TSP1 = m.addConstrs(sum(x_ij*adjacencyMatrix[i][j] for i in numPoints for j in numPoints if i!=j)==y_ik for k in trucksNum)
# #TSP2 = m.addConstrs( sum())
#
# m._vars = vars
# m.Params.lazyConstraints = 1
# m.optimize(subtourelim)
# # Retrieve solution
#
# vals = m.getAttr('x', x_ij)
# selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
#
# tour = subtour(selected)
# assert len(tour) == len(CLCto_retailers)