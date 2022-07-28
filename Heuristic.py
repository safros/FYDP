import numpy as np
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
            numTruck+=1
            # subtract the demand based on left over truck capacity
            remaining_Demand[nearest_neighbour] -= remaining_truck_capacity[numTruck]
            remaining_truck_capacity[numTruck] = 0
            #move to using the next truck
        elif remaining_Demand [nearest_neighbour] <= remaining_truck_capacity[numTruck]:
            indexNN = np.where(remaining_Cust == nearest_neighbour)
            remaining_Cust = np.delete(remaining_Cust, indexNN)
            remaining_truck_capacity[numTruck] -= remaining_Demand[nearest_neighbour]
            # then the demand of the customer has been satisfied and remove them from the remaining customer list
            remaining_Demand[nearest_neighbour] =0
            #subtract the demand from the remaining truck capacity
            if remaining_truck_capacity[numTruck]==0:
                numTruck+=1

truck_paths.update({0 : np.append(truck_paths.get(0),0)})
truck_paths.update({1 : np.append(truck_paths.get(1),0)})
truck_paths.update({2 : np.append(truck_paths.get(2),0)})
truck_paths.update({3 : np.append(truck_paths.get(3),0)})
print(truck_paths)