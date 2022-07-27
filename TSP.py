import gurobipy as gp
from gurobipy import GRB
import math
from itertools import combinations

#declare variables
demand_Retailer = [0,50,250,100] #the first entry is the depot
capacity_tuck_k= [100,100,250,250]
points=[0, 1, 2, 3] #where node 0 is the depot and 1,2,3 are the retailers
adjacencyMatrix = [[100000000, 16.3, 24.1, 14],
                       [16.3, 1000000000, 5.4, 5.2],
                       [24.1, 5.4, 100000000, 7.8],
                       [14, 5.2, 7.8, 1000000000]]

#cost $/km for ESAL damage based on vehicle
esal_k=[0.1, 0.1, 0.05, 0.05]

#cost of $/km for GHG damage based on vehicle
ghg_k = [0,0, 0.07334474, 0.07334474]

#Model initialize
m = gp.Model("Minimize Cost")

#number of vehicles
rangeNumVehicle = range(len(esal_k))

#ADD DECISION VARIABLES
#if we go from node i to node j with kth vehicle
x_ijk = {}
rangePoints= range(len(points))
for i in rangePoints:
    for j in rangePoints:
        #if (i!=j):
        for k in range(len(esal_k)):
            x_ijk[i, j, k] = m.addVar(vtype=GRB.BINARY, obj=(esal_k[k]+ghg_k[k])*adjacencyMatrix[i][j], name="xijk[%d,%d,%d]" % (i, j, k))

#y_ik ={}
#numTrucks = range(len(c_k))
#for i in rangePoints:
    #for k in range(len(c_k)):
        #y_ik [i,k] = m.addVar(vtype=GRB.BINARY, obj=0, name="yik[%d,%d]" % (i, k))

#The objective is to minimize the total fixed and variable costs
m.ModelSense = GRB.MINIMIZE

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                             if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(points):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                         <= len(tour)-1)

# Given a tuplelist of edges, find the shortest subtour
def subtour(edges):
    unvisited = points[:]
    cycle = points[:] # Dummy - guaranteed to be replaced
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle # New shortest subtour
    return cycle

#ADD CONSTRAINTS
#(1) each is assigned to a truck
#m.addConstrs((sum(x_ijk[i,j,k] for j in rangePoints if i!=j))== y_ik[i,k] for i in rangePoints for k in range(len(c_k)))

#(2) subtour elimination


#(3) number of paths away from the depot
#m.addConstrs(sum(y_ik[i,k] for i in range(1,3))== 1 )
#m.addConstr((sum(x_ijk[1,j,k] for j in rangePoints for k in range(len(c_k)) if j!=1)) == 4)

#(4) capacity and demand of retailer
#m.addConstrs( (sum(capacity_tuck_k[k]*y_ik[i,k] for k in numTrucks) == demand_Retailer[i] for i in range(0,3)))

#(5) number of paths into  the depot
#m.addConstr((sum(x_ijk[i,1,k] for i in rangePoints for k in range(len(c_k))if i!=1)) <= 4)

#MODEL 2 mTSP
#(2) each customer should be visited once by any vehicle if the customer is assigned to that the route of the vehicle
m.addConstrs((sum(x_ijk[i,j,k] for j in rangePoints for k in rangeNumVehicle))==1 for i in (1,3) )
#(3) each customer should be visited once by any vehicle if the customer is assigned to that the route of the vehicle
m.addConstrs((sum(x_ijk[i,j,k] for i in rangePoints for k in rangeNumVehicle))==1 for j in (1,3) )
#(4)exactly 1 vehicles depart from  to the depot
m.addConstrs((sum(x_ijk[i,0,k] for i in rangePoints ))==1 for k in rangeNumVehicle)
#(5) exactly 1 vehicles arrive to the depot
m.addConstrs((sum(x_ijk[0,j,k] for j in rangePoints ))==1 for k in rangeNumVehicle)
#(6) Truck capacity constraint where the demand of the customer is not more than the vehicle capacity
m.addConstrs((sum(demand_Retailer[j]*x_ijk[i,j,k] for i in rangePoints for j in rangePoints if i!=j))<= capacity_tuck_k[k] for k in rangeNumVehicle)
#(7)forbids the allocation of the same node by different vehicles
m.addConstrs((sum(x_ijk[i,j,k]*demand_Retailer[j] for i in rangePoints for j in rangePoints if i!=j)) - (sum(x_ijk[i,j,k]*demand_Retailer[i] for i in rangePoints for j in rangePoints if i!=j))==0 for k in rangeNumVehicle)

#subtour elimination from solving first time
#m.addConstrs(x_ijk[0,3,k]+x_ijk[3,0,k]<= 1 for k in rangeNumVehicle)
#m.addConstrs(x_ijk[1,2,k]+x_ijk[2,1,k]<= 1 for k in rangeNumVehicle)

m.update()

#SOLVE
m.optimize()
#m._vars = vars
#m.Params.lazyConstraints = 1
#m.optimize(subtourelim)

#PRINT SOLUTION
print('\nTOTAL COSTS: %g' % m.ObjVal)
print('SOLUTION:')

for i in rangePoints:
    for j in rangePoints:
        if (i!=j):
            for k in rangeNumVehicle:
                #print ((x_ijk[i,j,k].X))
                if ((x_ijk[i,j,k].X)==1) :
                    print(x_ijk[i, j, k].X)
                    print ("ijk: " + str(i)+" "+ str(j)+" "+str(k))

#for i in rangePoints:
    #for k in range(len(c_k)):
        #print (y_ik[i,k])


