import numpy as np
import random

#CONSTRUCTION HEURISTIC
#variable declare
truck_paths = {0:np.array([0]), 1:np.array([0]), 2:np.array([0]),3:np.array([0])}
truck_capacity = [100,100,250,250]
demand_Retailer = [50,250,100]
adjacencyMatrix = [[100000000, 16.3, 24.1, 14],
                       [16.3, 1000000000, 5.4, 5.2],
                       [24.1, 5.4, 100000000, 7.8],
                       [14, 5.2, 7.8, 1000000000]]
#cost $/km for ESAL damage based on vehicle
esal_k=[0.1, 0.1, 0.05, 0.05]
#cost of $/km for GHG damage based on vehicle
ghg_k = [0,0, 0.07334474, 0.07334474]

#initialize
remaining_Cust = np.array([0,1,2])
remaining_Demand = np.array([50,250,100])
remaining_truck_capacity = np.array([100,100,250,250])
currLocation = 0
numTruck = 0
loadPerTruck = {0:np.array([]),1:np.array([]),2:np.array([]),3:np.array([])}

#loop while there is still demand to be satisfied
while (remaining_Demand.any() and numTruck <4) :
    #check if the truck has more capacity
    while (remaining_Cust.any() ): #remaining_truck_capacity[numTruck]>0 and
        nearest_neighbour = remaining_Cust[0];
        min_cost = adjacencyMatrix[nearest_neighbour+1][currLocation]*(esal_k[numTruck]+ghg_k[numTruck])
        # find the closest customer
        for rc in remaining_Cust:
            if (adjacencyMatrix[rc+1] [currLocation]*(esal_k[numTruck]+ghg_k[numTruck])< min_cost):
                #this is the customer we want to add to the path
                nearest_neighbour = rc
                min_cost =adjacencyMatrix[rc] [currLocation]*(esal_k[numTruck]+ghg_k[numTruck])
        #add the customer to the path of the truck
        truck_paths.update({numTruck : np.append(truck_paths.get(numTruck),nearest_neighbour+1)})
        #update current location
        currLocation = nearest_neighbour+1
        #if the demand of the customer > remaining truck capacity
        #if the remain truck capacity >= demand of customer
        if remaining_Demand [nearest_neighbour] > remaining_truck_capacity[numTruck]:
            loadPerTruck.update({numTruck: np.append(loadPerTruck.get(numTruck), remaining_truck_capacity[numTruck])})
            # subtract the demand based on left over truck capacity
            remaining_Demand[nearest_neighbour] -= remaining_truck_capacity[numTruck]
            remaining_truck_capacity[numTruck] = 0
            numTruck += 1
            #move to using the next truck
        elif remaining_Demand [nearest_neighbour] <= remaining_truck_capacity[numTruck]:
            indexNN = np.where(remaining_Cust == nearest_neighbour)
            remaining_Cust = np.delete(remaining_Cust, indexNN)
            remaining_truck_capacity[numTruck] -= remaining_Demand[nearest_neighbour]
            loadPerTruck.update({numTruck : np.append(loadPerTruck.get(numTruck),remaining_Demand[nearest_neighbour])})
            # then the demand of the customer has been satisfied and remove them from the remaining customer list
            remaining_Demand[nearest_neighbour] =0
            #subtract the demand from the remaining truck capacity
            if remaining_truck_capacity[numTruck]==0:
                numTruck+=1

truck_paths.update({0 : np.append(truck_paths.get(0),0)})
truck_paths.update({1 : np.append(truck_paths.get(1),0)})
truck_paths.update({2 : np.append(truck_paths.get(2),0)})
truck_paths.update({3 : np.append(truck_paths.get(3),0)})

objValue = 0
costPerTruckPath = np.array([0.0,0.0,0.0,0.0])
for truck in range(0, 4):
    truckVal=0
    currPathtoCalc =truck_paths.get(truck).copy()
    if  not np.any(currPathtoCalc):
        #this truck was not used go to next truck
        print("truck " + str(truck+1) + " was not used")
    else :
        b = len(currPathtoCalc)
        for p in range(b-1):
            a=currPathtoCalc[p]
            b=currPathtoCalc [p+1]
            objValue = objValue + adjacencyMatrix[a][b]*(esal_k[truck]+ghg_k[truck])
            truckVal = truckVal + adjacencyMatrix[a][b]*(esal_k[truck]+ghg_k[truck])
        costPerTruckPath[truck] = truckVal

print("paths of trucks: ")
print(truck_paths)
print("Objective value: ")
print(objValue)
print("cost for each truck path: ")
print(costPerTruckPath)
print("load/truck: ")
print(loadPerTruck)
print()

#IMPROVEMENT HEURISTIC
#intra-route 2 opt switch
opti_truckpaths = {0:np.array([]), 1:np.array([]), 2:np.array([])}
incumbent2_Opt= []
incumbent_switch ={}
incumbent_truckSwap ={}

#intra-route 2-opt switch
for truck in range(0, 4):
    currPath = truck_paths.get(truck).copy()
    #if there is more than 3 elements in the array
    if len(currPath) > 3:
        min_dist = costPerTruckPath[truck]
        b = len(currPath)
        for looping in range(0,10):
            # pick 2 random nodes in side truck path and swap the nodes
            n1 = random.randint(1, b - 2)
            n2 = random.randint(1, b - 2)
            if n2 > n1:
                currPath[n1], currPath[n2] = currPath[n2], currPath[n1]
            elif n1 > n2:
                currPath[n2], currPath[n1] = currPath[n1], currPath[n2]
            else:
                if n2 == n1:
                    n2 = n2 - 1
                    currPath[n2], currPath[n1] = currPath[n1], currPath[n2]
            # get new distance
            distanceSum = 0
            for m in range(b-1):
                a = currPath[m]
                q = currPath[m + 1]
                distanceSum = distanceSum + adjacencyMatrix[a][q]*(esal_k[truck]+ghg_k[truck])
            if distanceSum < min_dist:
                min_dist= distanceSum
                incumbent2_Opt = currPath.copy()
            else:
                if len(incumbent2_Opt)==0:
                    currPath = truck_paths.get(truck).copy()
                else:
                    currPath= incumbent2_Opt.copy()
        # save the incumbent into the dictionary
        # reset the incumbent for the next truck path opti
        opti_truckpaths[truck] = currPath.copy()
        incumbent2_Opt = []

print(opti_truckpaths)

def checkCapacity (route1, route2, r1, r2) :
    if not np.any(loadPerTruck[r2]):
        #truck is not being used
        capacity_needed = loadPerTruck[r1][n1 - 1]
        t_capacityLeft = truck_capacity[r2]
        if capacity_needed > t_capacityLeft:
            return False
        return True
    elif not np.any(loadPerTruck[r1]):
        # truck is not being used
        capacity_needed = loadPerTruck[r2][n2 - 1]
        t_capacityLeft = truck_capacity[r1]
        if capacity_needed > t_capacityLeft:
            return False
        return True
    else:
        tl = 0
        for j in loadPerTruck[r2]:
            tl += j

        if truck_capacity[r2]<= tl-loadPerTruck[r2][n2-1]+loadPerTruck[r1][n1 - 1]:
            return False

        tl = 0
        for j in loadPerTruck[r1]:
            tl += j

        if truck_capacity[r1]<= tl-loadPerTruck[r1][n1-1]+loadPerTruck[r2][n2 - 1]:
            return False

    return True

def getCost (route, truck):
    cost = 0
    if  not np.any(route):
        #this truck was not used go to next truck
        print("truck " + str(truck+1) + " was not used")
        return 0
    else :
        b = len(route)
        for p in range(b-1):
            a=route[p]
            b=route [p+1]
            cost = cost + adjacencyMatrix[a][b]*(esal_k[truck]+ghg_k[truck])
        return cost

curr_truck_paths = truck_paths.copy()
incumbent_switch = truck_paths.copy()
#exchange or add into routes
for looping in range(0,100):
    # pick 2 random truck routes
    r1 = random.randint(0, 3)
    r2 = random.randint(0, 3)
    if r1==r2 :
        if r1!=0:
            r1-=1
        elif r2!=0 :
            r2-=1
        else :
            r1+=1
    #curr min distance
    min_cost = costPerTruckPath[r1]+costPerTruckPath[r2]
    #now we have two different routes
    route1 = curr_truck_paths.get(r1).copy()
    len_route1 = len(route1)
    route2 = curr_truck_paths.get(r2).copy()
    len_route2= len(route2)
    #pick a node to swap
    if len_route1==2 or len_route2==2:
        #picked a truck that was not in use
        #NOTE IF THERE IS MORE THAN ONE TRUCK NOT IN USE THIS LOGIC NEEDS TO BE REDONE
        if len_route1==2:
            n2 = random.randint(1, len_route2 - 2)
            node2 = route2[n2]
            node1 =0
            n1=0
        if len_route2==2:
            n1 = random.randint(1, len_route1 - 2)
            node1 = route1[n1]
            node2=0
            n2=0
    else:
        n1= random.randint(1, len_route1-2)
        n2 = random.randint(1, len_route2 - 2)
        node1 = route1[n1]
        node2 = route2[n2]
    if node1!=node2:
        if node1 in route2 or node2 in route1:
            print("don't switch already in path")
        else:
            #switch the node
            if not np.any(route1) or not np.any(route2):
                #this truck was not used just do a change not a swap
                if not np.any(route1):
                    route1 = np.insert(route1, 1, node2)
                    route2 = np.delete(route2, n2)
                else:
                    route2 = np.insert(route2, 1, node1)
                    route1 = np.delete(route1, n1)
            else:
                route1[n1] = node2
                route2[n2] =node1
            #check capacity and demand constraints
            demandSatisfied = checkCapacity(route1, route2, r1, r2)
            if (demandSatisfied):
                #calc the distance
                costR1 = getCost(route1, r1)
                costR2 = getCost(route2, r2)
                newCost = costR1+costR2
                if newCost<min_cost :
                    #NEW BEST
                    incumbent_switch = curr_truck_paths.copy()
                    incumbent_switch[r1] = route1
                    incumbent_switch[r2] = route2
                    #min_cost=newCost
                    costPerTruckPath[r1] = costR1
                    costPerTruckPath[r2] = costR2
                    #update the truck load
                else:
                    if len(incumbent_switch)==0:
                        curr_truck_paths = truck_paths.copy()
                    else:
                        curr_truck_paths= incumbent_switch.copy()
            else:
                print("demand not satisfied")
                #if I cannot satisfy demand of the customer I shouldn't swap
    else:
        #node are equal skip???
        print("nodes are equal/this node is already in the path of the truck")
        #capacity left on truck
        capacity_needed = loadPerTruck [r1][n1-1]+loadPerTruck[r2][n2-1]
        tl=0
        for j in loadPerTruck[r1]:
            tl += j
        t_capacityLeft = truck_capacity[r1]- tl+loadPerTruck [r1][n1-1]
        if  capacity_needed<= t_capacityLeft:
            route2 = np.delete(route2, n2)
            loadPerTruck[r1][n1-1] += loadPerTruck[r2][n2-1]
            loadPerTruck[r2][n2 - 1] = 0
            #if the truck has enough capacity to take the customer completely from the other path
            #then give that entire customer to that truck
        tl = 0
        for j in loadPerTruck[r2]:
            tl += j
        t_capacityLeft = truck_capacity[r2] - tl + loadPerTruck[r2][n2 - 1]
        if capacity_needed <= t_capacityLeft:
            route1 = np.delete(route1, n1)
            loadPerTruck[r2][n2 - 1] += loadPerTruck[r1][n1 - 1]
            loadPerTruck[r1][n1 - 1] = 0
            # if the truck has enough capacity to take the customer completely from the other path
            # then give that entire customer to that truck
        costR1 = getCost(route1, r1)
        costR2 = getCost(route2, r2)
        newCost = costR1 + costR2
        if newCost < min_cost:
            incumbent_switch[r1] = route1
            incumbent_switch[r2] = route2
            #min_cost = newCost
            costPerTruckPath[r1] = costR1
            costPerTruckPath[r2]=costR2
        else:
            if len(incumbent_switch) == 0:
                print()
                #curr_truck_paths = truck_paths.copy()
            else:
                print()
                #curr_truck_paths = incumbent_switch.copy()

print(incumbent_switch)
