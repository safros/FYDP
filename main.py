#main.py
#https://gist.github.com/dasdachs/69c42dfcfbf2107399323a4c86cdb791
import os
import csv
from io import TextIOWrapper
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random2
import folium
import capstone
from capstone import dijkstra_algorithm, print_result
import osmnx as ox
import networkx as nx
from openpyxl import Workbook

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.app_context().push()

class DataForModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.String(80), unique=True)
    distance = db.Column(db.String(80), unique=True)
    truck = db.Column(db.String(80), unique=True)
    demand = db.Column(db.Integer(), unique=True)

    def __repr__(self):
        return "<Cost: {}>".format(self.cost)


@app.route("/", methods=('GET','POST'))

def index ():
    if request.method == 'POST':
        csv_file = request.files['file']
        #csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        #csv_reader = csv.reader(csv_file, delimiter=',')
        startData = pd.read_excel(csv_file, 'start')
        distanceData = pd.read_excel(csv_file, 'distance')
        truckData = pd.read_excel(csv_file, 'truck')
        demandData = pd.read_excel(csv_file,'demand')
        damagesData = pd.read_excel(csv_file, 'damages')
        speedData = pd.read_excel(csv_file, 'speedLimit')
        emissionsData = pd.read_excel(csv_file, 'emissions')
        lookUpData = pd.read_excel(csv_file, 'nodeLookUp')
        #for row in csv_reader:
        #user = User(username=row[0], email=row[1])
        #db.session.add(user)
        #dataDB = DataForModel(cost=row[0])
        #db.session.add(dataDB)
        startData.to_sql('currlocation', con=db.engine, if_exists='replace', index_label='id')
        distanceData.to_sql('distance', con=db.engine, if_exists='replace', index_label='id')
        truckData.to_sql('truck', con=db.engine, if_exists='replace', index_label='id')
        demandData.to_sql('demand', con=db.engine, if_exists='replace', index_label='id')
        damagesData.to_sql('damages', con=db.engine, if_exists='replace', index_label='id')
        speedData.to_sql('speedLimit', con=db.engine, if_exists='replace', index_label='id')
        emissionsData.to_sql('emissions', con=db.engine, if_exists='replace', index_label='id')
        lookUpData.to_sql('lookUp', con=db.engine, if_exists='replace', index_label='id')

        list = db.engine.execute("SELECT * FROM truck").fetchall()
        print(list)
        db.session.commit()
        return render_template('runModelButton.html')#render_template('dbview.html',list=list)

    return render_template('index.html')

@app.route("/instructions")
def instructions():
    return render_template('instructions.html')

@app.route("/model")
def display():
    return render_template('model.html')

@app.route("/dbview")
def viewEntries ():
    list = db.engine.execute("SELECT * FROM truck").fetchall()
    #pritn names of columns to check
    #data = db.engine.execute('''SELECT * FROM truck''')
    #row = data.fetchone()
    #names = row.keys()
    #print(names)
    return render_template('dbview.html',list=list)

@app.route("/run_model",methods=('GET','POST'))
def runModel ():
    #run model on the data
    #call dijstra's algorithm on the data to create the adj matrix and the shortest path mapping
    adjacencymatrix = dijstra()
    #call heuristic
    anArray = heuristic()

    #display a map of the final solution
    map1 = folium.Map(location=[43.40205, -80.5])
    body_html = map1.get_root().html.render()
    #map1.save("./templates/map.html")
    map1.get_root().width = "1500px"
    map1.get_root().height = "800px"
    rand_color=['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    #for s in range(1,anArray[3]):
        #rand_color.append("%06x" % random2.randint(0, 0xFFFFFF))
    for s in range(0,anArray[3]-1):
        pathTruck= anArray[0].get(s)
        if pathTruck.size>2: #the truck is used
            for i in range(0,pathTruck.size-2):
                actualOrigin= anArray[1].get(pathTruck[i])
                actualDestination = anArray[1].get(pathTruck[i+1])
                origin_node=getLatAndLog(actualOrigin)
                destination_node=getLatAndLog(actualDestination)
                loc=[(origin_node[0],origin_node[1]),(destination_node[0],destination_node[1])]
                folium.PolyLine(loc, color=rand_color[s],weight=15, opacity=0.8).add_to(map1)
    iframe = map1.get_root()._repr_html_()
    return render_template('runModel.html', iframe=iframe,)

@app.route("/compareEVtoNonEV")
def compare():
    # display a map with the shortest paths displayed between EV and Non-EVs
    map2 = folium.Map(location=[43.40205, -80.5])
    body_html = map2.get_root().html.render()
    #map1.save("./templates/map.html")
    map2.get_root().width = "1500px"
    map2.get_root().height = "800px"
    #adapted from https://stackoverflow.com/questions/60578408/is-it-possible-to-draw-paths-in-folium
    ox.config(log_console=True, use_cache=True)
    G_drive = ox.graph_from_place('Kitchener, Ontario, Canada',
                                 network_type='drive')
    #for every demand node to every other demand node
    #get the path from mapdictionary
    #draw each path with origin and destination nodes
    #add to the map
    mapDictionaryDamages = db.engine.execute("SELECT * FROM MapDictionaryDamages").fetchall()
    mapDictionaryEmissions = db.engine.execute("SELECT * FROM MapDictionaryEmissions").fetchall()
    exceptSQLresult = db.engine.execute("SELECT * FROM MapDictionaryDamages Except SELECT * FROM MapDictionaryEmissions")
    route=[]
    for s in mapDictionaryDamages:
        pairing = s[0]
        nonEVPath=[]
        for i in s[1:]:
            if i is not None:
                nonEVPath.append(i)
            else:
                break

        #loop over the list
        for i in range(0,len(nonEVPath)-1):
            #get the latitude and longitude for the list
            orig_node= getLatAndLog(nonEVPath[i])
            dest_node=getLatAndLog(nonEVPath[i+1])
            loc = [(orig_node[0], orig_node[1]), (dest_node[0], dest_node[1])]
            folium.PolyLine(loc,
                        color='red',
                        weight=15,
                        opacity=0.6).add_to(map2)
    for s in mapDictionaryEmissions:
        pairing = s[0]
        EVPath = []
        #orig_node = ox.nearest_nodes(G_drive, 40.748441, -73.4)
        #dest_node = ox.nearest_nodes(G_drive,40.748441, -73.4)
        #route.append(nx.shortest_path(G_drive,orig_node, dest_node,weight=2))
        for i in s[1:]:
            if i is not None:
                EVPath.append(i)
            else:
                break

        # loop over the list
        for i in range(0, len(EVPath) - 1):
            # get the latitude and longitude for the list
            orig_node = getLatAndLog(EVPath[i])
            dest_node = getLatAndLog(EVPath[i + 1])
            loc = [(orig_node[0], orig_node[1]), (dest_node[0], dest_node[1])]
            folium.PolyLine(loc,
                            color='blue',
                            weight=15,
                            opacity=0.6).add_to(map2)

    #map2 = ox.plot_route_folium(G_drive, route)
    iframe = map2.get_root()._repr_html_()
    return render_template('compare.html', iframe=iframe)

#get the latitude and logitude of any point if given the node_id
def getLatAndLog (currLocation):
    datanodelookup = db.engine.execute("SELECT * FROM lookUp where lookup_ID ={}".format(currLocation)).fetchall()
    for s in datanodelookup:
        latnum = float(s[2])
        lognum = float(s[3])
    return  latnum,lognum

def heuristic():
    numTrucksTotal = db.engine.execute("select count(*) from truck").fetchall()
    numTrucksTotal=numTrucksTotal[0]._data[0]
    #truck_paths = {0: np.array([0]), 1: np.array([0]), 2: np.array([0]), 3: np.array([0])}
    #make the truck paths dynamically
    truck_paths={}
    for i in range(0,numTrucksTotal):
        truck_paths[i] = np.array([0])

    datatruck_capacity = db.engine.execute("SELECT capacity FROM truck").fetchall()
    truck_capacity=[]
    for s in datatruck_capacity:
        truck_capacity=np.append(truck_capacity,int(s[0]))

    datademand_Retailer = db.engine.execute("SELECT demand_units FROM demand").fetchall()
    demand_Retailer=[]
    for s in datademand_Retailer:
        demand_Retailer=np.append(demand_Retailer,int(s[0]))

    dataadjacencyMatrix = db.engine.execute("SELECT * FROM adjMatrixDamages").fetchall()
    adjacencyMatrixDamage=make_adjMatrix(dataadjacencyMatrix)

    #for ESAL damage based on vehicle, mutiply the adj cost matrix by esal in truck table
    dataESAL = db.engine.execute("SELECT esal FROM truck").fetchall()
    esal_k = []
    truckType = []
    numNonEv=0
    for s in dataESAL:
        if s._data[0] is None:
            #NON ev value
            numNonEv=numNonEv+1
            #esal_k.append(int(s[0]))
            esal_k.append(2)
        else:
            esal_k.append(int(s[0]))
            truckType.append('EV')
    # cost of $/km for emissions based on the type of truck get the cost matrix
    #ghg_k = [0, 0, 0.07334474, 0.07334474]
    datatruckType = db.engine.execute("SELECT type FROM truck").fetchall()
    for s in datatruckType:
        if str(s[0]) =='Single Unit Long Haul':
            print('get matrix 1')
            matrixTruck1data =db.engine.execute("SELECT * FROM adjMatrixEmissions").fetchall()
            adjMatrixTruck1 = make_adjMatrix(matrixTruck1data)
            truckType.append('Single Unit Long Haul')
            esal_k.append(0)
        elif str(s[0]) =='Single Unit Short Haul':
            print('matrix 2')
            matrixTruck2data=db.engine.execute("SELECT * FROM adjMatrixEmissionsTruckType2").fetchall()
            adjMatrixTruck2 = make_adjMatrix(matrixTruck2data)
            truckType.append('Single Unit Short Haul')
            esal_k.append(0)
        elif str(s[0]) =='Combination Short Haul':
            print('matrix 3')
            matrixTruck3data=db.engine.execute("SELECT * FROM adjMatrixEmissionsTruckType3").fetchall()
            adjMatrixTruck3 = make_adjMatrix(matrixTruck3data)
            truckType.append('Combination Short Haul')
            esal_k.append(0)

    # initialize
    dataremaining_Cust = np.array(db.engine.execute("SELECT node_id FROM demand").fetchall())
    remaining_CustTmp=[]
    #customerNode =[]
    indexFinder= {}
    idxer=0
    for s in dataremaining_Cust:
        #customerNode=np.append(customerNode,int(s[0]))
        remaining_CustTmp.append(idxer)
        indexFinder[idxer]=int(s[0])
        idxer=idxer+1
    remaining_Cust=np.array(remaining_CustTmp)
    dataremaining_Demand = np.array(db.engine.execute("SELECT demand_units FROM demand").fetchall())
    remaining_DemandTmp=[]
    for s in dataremaining_Demand:
        remaining_DemandTmp.append(int(s[0]))
    remaining_Demand=np.array(remaining_DemandTmp)
    dataremaining_truck_capacity = np.array(db.engine.execute("SELECT capacity FROM truck").fetchall())
    remaining_truck_capacity = []
    for s in dataremaining_truck_capacity:
        remaining_truck_capacity = np.append(remaining_truck_capacity, int(s[0]))
    #datacurrLocation = db.engine.execute("SELECT clcLocation FROM currlocation").fetchall()
    #for s in datacurrLocation:
        #currLocation=int(s[0])
    currLocation =0
    numTruck = 0
    #loadPerTruck = {0: np.array([]), 1: np.array([]), 2: np.array([]), 3: np.array([])}
    # make the truck paths dynamically
    loadPerTruck = {}
    for i in range(0, numTrucksTotal):
        loadPerTruck[i] = np.array([])
    #print("truck capacity: IS IT OK?")
    #print(truck_capacity)

    while (remaining_Demand.any() and numTruck < numTrucksTotal):
        # check if the truck has more capacity
        #get the truck's adjmatrix
        if truckType[numTruck]=='Single Unit Long Haul':
            adjacencyMatrix=adjMatrixTruck1
        elif truckType[numTruck]=='Single Unit Short Haul':
            adjacencyMatrix =adjMatrixTruck2
        elif truckType[numTruck]=='Combination Short Haul':
            adjacencyMatrix = adjMatrixTruck3
        else: #the truck is an EV with no emissions matrix that is a 0 matrix
            adjacencyMatrix=np.zeros((len(remaining_Cust)+1,len(remaining_Cust)+1))

        while (remaining_Cust.any()):  # remaining_truck_capacity[numTruck]>0 and
            nearest_neighbour = remaining_Cust[0];
            #find the index of the remaining customer
            #nearest_neighbour = indexFinder.index(nearest_neighbour)
            min_cost = adjacencyMatrix[nearest_neighbour + 1][currLocation]+ esal_k[numTruck]*adjacencyMatrixDamage[nearest_neighbour + 1][currLocation]
            #min_cost=adjacencyMatrix[nearest_neighbour + 1][currLocation] * (esal_k[numTruck] + ghg_k[numTruck])
            # find the closest customer
            for rc in remaining_Cust:
                if (adjacencyMatrix[rc + 1][currLocation]+ esal_k[numTruck]*adjacencyMatrixDamage[rc + 1][currLocation]< min_cost):
                    #(adjacencyMatrix[rc + 1][currLocation] * (esal_k[numTruck] + ghg_k[numTruck]) < min_cost):
                    # this is the customer we want to add to the path
                    nearest_neighbour = rc
                    #nearest_neighbour = indexFinder.index(nearest_neighbour)
                    #min_cost = adjacencyMatrix[rc][currLocation] * (esal_k[numTruck] + ghg_k[numTruck])
                    min_cost = adjacencyMatrix[rc][currLocation]+esal_k[numTruck]*adjacencyMatrixDamage[rc][currLocation]
            # add the customer to the path of the truck
            truck_paths.update({numTruck: np.append(truck_paths.get(numTruck), nearest_neighbour)})
            # update current location
            currLocation = nearest_neighbour + 1
            # if the demand of the customer > remaining truck capacity
            # if the remain truck capacity >= demand of customer
            if remaining_Demand[nearest_neighbour] > remaining_truck_capacity[numTruck]:
                loadPerTruck.update(
                    {numTruck: np.append(loadPerTruck.get(numTruck), remaining_truck_capacity[numTruck])})
                # subtract the demand based on left over truck capacity
                remaining_Demand[nearest_neighbour] -= remaining_truck_capacity[numTruck]
                remaining_truck_capacity[numTruck] = 0
                numTruck += 1
                # move to using the next truck
            elif remaining_Demand[nearest_neighbour] <= remaining_truck_capacity[numTruck]:
                indexNN = np.where(remaining_Cust == nearest_neighbour)
                remaining_Cust = np.delete(remaining_Cust, indexNN)
                remaining_truck_capacity[numTruck] -= remaining_Demand[nearest_neighbour]
                loadPerTruck.update(
                    {numTruck: np.append(loadPerTruck.get(numTruck), remaining_Demand[nearest_neighbour])})
                # then the demand of the customer has been satisfied and remove them from the remaining customer list
                remaining_Demand[nearest_neighbour] = 0
                # subtract the demand from the remaining truck capacity
                if remaining_truck_capacity[numTruck] == 0:
                    numTruck += 1

    #truck_paths.update({0: np.append(truck_paths.get(0), 0)})
    #truck_paths.update({1: np.append(truck_paths.get(1), 0)})
    #truck_paths.update({2: np.append(truck_paths.get(2), 0)})
    #truck_paths.update({3: np.append(truck_paths.get(3), 0)})
    dataStartNode = db.engine.execute("SELECT clcLocation FROM currlocation").fetchall()
    for s in dataStartNode:
        CLCstart= int(s[0])
    #for i in range(0,numTrucksTotal):
        #truck_paths.update({i:np.append(truck_paths.get(i), CLCstart)})

    objValue = 0
    #costPerTruckPath = np.array([0.0, 0.0, 0.0, 0.0])
    costPerTruckPath=np.zeros(numTrucksTotal)

    for truck in range(0, numTrucksTotal):
        truckVal = 0
        currPathtoCalc = truck_paths.get(truck).copy()
        if not np.any(currPathtoCalc):
            # this truck was not used go to next truck
            print("truck " + str(truck + 1) + " was not used")
        else:
            b = len(currPathtoCalc)
            for p in range(b - 2):
                a = currPathtoCalc[p]
                b = currPathtoCalc[p + 1]
                #objValue = objValue + adjacencyMatrix[a][b] * (esal_k[truck] + ghg_k[truck])
                objValue = objValue + adjacencyMatrix[a][b]+esal_k[truck]*adjacencyMatrixDamage[a][b]
                #truckVal = truckVal + adjacencyMatrix[a][b] * (esal_k[truck] + ghg_k[truck])
                truckVal=truckVal + adjacencyMatrix[a][b]+esal_k[truck]*adjacencyMatrixDamage[a][b]
            costPerTruckPath[truck] = truckVal

    print("paths of trucks: ")
    print(truck_paths)
    print(indexFinder)
    print("Objective value: ")
    print(objValue)
    print("cost for each truck path: ")
    print(costPerTruckPath)
    print("load/truck: ")
    print(loadPerTruck)
    print()

    # IMPROVEMENT HEURISTIC
    # intra-route 2 opt switch
    #opti_truckpaths = {0: np.array([]), 1: np.array([]), 2: np.array([])}
    opti_truckpaths = {}
    for i in range(0, numTrucksTotal):
        opti_truckpaths[i] = np.array([])
    incumbent2_Opt = []
    incumbent_switch = {}
    incumbent_truckSwap = {}

    # intra-route 2-opt switch
    for truck in range(0, numTrucksTotal):
        currPath = truck_paths.get(truck).copy()
        # if there is more than 3 elements in the array
        if len(currPath) > 3:
            min_dist = costPerTruckPath[truck]
            b = len(currPath)
            for looping in range(0, 10):
                # pick 2 random nodes in side truck path and swap the nodes
                n1 = random2.randint(1, b - 2)
                n2 = random2.randint(1, b - 2)
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
                for m in range(b - 1):
                    a = currPath[m]
                    q = currPath[m + 1]
                    #distanceSum = distanceSum + adjacencyMatrix[a][q] * (esal_k[truck] + ghg_k[truck])
                    distanceSum = distanceSum + adjacencyMatrix[a][q]+esal_k[truck]*adjacencyMatrixDamage[a][q]
                if distanceSum < min_dist:
                    min_dist = distanceSum
                    incumbent2_Opt = currPath.copy()
                else:
                    if len(incumbent2_Opt) == 0:
                        currPath = truck_paths.get(truck).copy()
                    else:
                        currPath = incumbent2_Opt.copy()
            # save the incumbent into the dictionary
            # reset the incumbent for the next truck path opti
            opti_truckpaths[truck] = currPath.copy()
            incumbent2_Opt = []

    print(opti_truckpaths)

    def checkCapacity(route1, route2, r1, r2):
        if not np.any(loadPerTruck[r2]):
            # truck is not being used
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

            if truck_capacity[r2] <= tl - loadPerTruck[r2][n2 - 1] + loadPerTruck[r1][n1 - 1]:
                return False

            tl = 0
            for j in loadPerTruck[r1]:
                tl += j

            if truck_capacity[r1] <= tl - loadPerTruck[r1][n1 - 1] + loadPerTruck[r2][n2 - 1]:
                return False

        return True

    def getCost(route, truck):
        cost = 0
        if not np.any(route):
            # this truck was not used go to next truck
            print("truck " + str(truck + 1) + " was not used")
            return 0
        else:
            b = len(route)
            for p in range(b - 1):
                a = route[p]
                b = route[p + 1]
                #cost = cost + adjacencyMatrix[a][b] * (esal_k[truck] + ghg_k[truck])
                cost=cost + adjacencyMatrix[a][b]+esal_k[truck]*adjacencyMatrixDamage[a][b]
            return cost

    curr_truck_paths = truck_paths.copy()
    incumbent_switch = truck_paths.copy()
    numTrucksInUse=0
    for s in truck_paths.keys():
        if truck_paths[s].size>2:
            #truck in use
            numTrucksInUse=numTrucksInUse+1
    # exchange or add into routes
    for looping in range(0, 100):
        # pick 2 random truck routes
        r1 = random2.randint(0, numTrucksInUse-1)
        r2 = random2.randint(0, numTrucksInUse-1)
        if r1 == r2:
            if r1 != 0:
                r1 -= 1
            elif r2 != 0:
                r2 -= 1
            else:
                if r1==numTrucksInUse:
                    r1-=1
                else:
                    r1+=1
        # curr min distance
        min_cost = costPerTruckPath[r1] + costPerTruckPath[r2]
        # now we have two different routes
        route1 = curr_truck_paths.get(r1).copy()
        len_route1 = len(route1)
        route2 = curr_truck_paths.get(r2).copy()
        len_route2 = len(route2)
        # pick a node to swap
        n1 = random2.randint(1, len_route1-1)
        n2 = random2.randint(1, len_route2-1)
        node1 = route1[n1]
        node2 = route2[n2]
        if node1 != node2:
            if node1 in route2 or node2 in route1:
                print("don't switch already in path")
            else:
                # switch the node
                if not np.any(route1) or not np.any(route2):
                    # this truck was not used just do a change not a swap
                    if not np.any(route1):
                        route1 = np.insert(route1, 1, node2)
                        route2 = np.delete(route2, n2)
                    else:
                        route2 = np.insert(route2, 1, node1)
                        route1 = np.delete(route1, n1)
                else:
                    route1[n1] = node2
                    route2[n2] = node1
                # check capacity and demand constraints
                demandSatisfied = checkCapacity(route1, route2, r1, r2)
                if (demandSatisfied):
                    # calc the distance
                    costR1 = getCost(route1, r1)
                    costR2 = getCost(route2, r2)
                    newCost = costR1 + costR2
                    if newCost < min_cost:
                        # NEW BEST
                        incumbent_switch = curr_truck_paths.copy()
                        incumbent_switch[r1] = route1
                        incumbent_switch[r2] = route2
                        # min_cost=newCost
                        costPerTruckPath[r1] = costR1
                        costPerTruckPath[r2] = costR2
                        # update the truck load
                    else:
                        if len(incumbent_switch) == 0:
                            curr_truck_paths = truck_paths.copy()
                        else:
                            curr_truck_paths = incumbent_switch.copy()
                else:
                    print("demand not satisfied")
                    # if I cannot satisfy demand of the customer I shouldn't swap
        else:
            # node are equal skip???
            print("nodes are equal/this node is already in the path of the truck")
            # capacity left on truck
            capacity_needed = loadPerTruck[r1][n1 - 1] + loadPerTruck[r2][n2 - 1]
            tl = 0
            for j in loadPerTruck[r1]:
                tl += j
            t_capacityLeft = truck_capacity[r1] - tl + loadPerTruck[r1][n1 - 1]
            if capacity_needed <= t_capacityLeft:
                route2 = np.delete(route2, n2)
                loadPerTruck[r1][n1 - 1] += loadPerTruck[r2][n2 - 1]
                loadPerTruck[r2][n2 - 1] = 0
                # if the truck has enough capacity to take the customer completely from the other path
                # then give that entire customer to that truck
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
                # min_cost = newCost
                costPerTruckPath[r1] = costR1
                costPerTruckPath[r2] = costR2
            else:
                if len(incumbent_switch) == 0:
                    print()
                    # curr_truck_paths = truck_paths.copy()
                else:
                    print()
                    # curr_truck_paths = incumbent_switch.copy()

    print(incumbent_switch)

    return truck_paths,indexFinder, objValue, numTrucksTotal

def dijstra ():
    #get all the data needed for the graph
    nodes=[]
    dataLookUp = db.engine.execute("SELECT * FROM lookUp").fetchall()
    dataDamages = db.engine.execute("SELECT * FROM damages").fetchall()
    dataDistances=db.engine.execute("SELECT * FROM distance").fetchall()
    dataDemand = db.engine.execute("SELECT node_id FROM demand").fetchall()
    dataStartNode = db.engine.execute("SELECT clcLocation FROM currlocation").fetchall()
    init_graph_Damages = {}
    init_graph_Emissions={}
    init_graph_EmissionsTruckType2 = {}
    init_graph_EmissionsTruckType3 = {}
    for row in dataLookUp:
        nodes.append(str(row[1]))
        #print(row)

    for node in nodes:
        init_graph_Damages[node] = {}
        init_graph_Emissions[node] = {}
        init_graph_EmissionsTruckType2[node] = {}
        init_graph_EmissionsTruckType3[node] = {}

    #add the costs to the graph
    for row in dataDamages:
        init_graph_Damages[str(int(row[1]))][str(int(row[2]))] = float(row[3])

    for row in dataDistances:
        # fetch the speed corresponding to the correct origin destination
        speedNeeded =db.engine.execute("SELECT Speed_Limit FROM speedLimit WHERE Origin_ID LIKE '{}' AND Destination_ID LIKE '{}'".format(str(row[1]), str(row[2]))).fetchall()
        for s in speedNeeded:
            lookSpeed = str(s[0])
        #take that speed and get the correct emissions for exactly one type of truck
        dataEmissions = db.engine.execute(
            "SELECT costperKm FROM emissions WHERE typeTruck LIKE 'Single Unit Short Haul' AND speed LIKE '{}' AND gasVDiesel LIKE 'diesel'".format(lookSpeed)).fetchall()
        for s in dataEmissions:
            lookE = float(s[0])
        init_graph_Emissions[str(int(row[1]))][str(int(row[2]))] = float(row[3])*float(lookE)

        dataEmissions = db.engine.execute(
            "SELECT costperKm FROM emissions WHERE typeTruck LIKE 'Single Unit Long Haul' AND speed LIKE '{}' AND gasVDiesel LIKE 'diesel'".format(
                lookSpeed)).fetchall()
        for s in dataEmissions:
            lookE = float(s[0])
        init_graph_EmissionsTruckType2[str(int(row[1]))][str(int(row[2]))] = float(row[3]) * float(lookE)

        dataEmissions = db.engine.execute(
            "SELECT costperKm FROM emissions WHERE typeTruck LIKE 'Combination Long Haul' AND speed LIKE '{}' AND gasVDiesel LIKE 'diesel'".format(
                lookSpeed)).fetchall()
        for s in dataEmissions:
            lookE = float(s[0])
        init_graph_EmissionsTruckType3[str(int(row[1]))][str(int(row[2]))] = float(row[3]) * float(lookE)

    graphDamage = capstone.Graph(nodes, init_graph_Damages)
    graphEmission = capstone.Graph(nodes, init_graph_Emissions)
    graphEmissionTruck2 = capstone.Graph(nodes, init_graph_Emissions)
    graphEmissionTruck3 = capstone.Graph(nodes, init_graph_Emissions)
    #previous_nodes, shortest_path = dijkstra_algorithm(graph=graphDamage, start_node="1")
    #previous_nodes1, shortest_path1 = dijkstra_algorithm(graph=graphEmission, start_node="1")
    #for each node in the demand find the path that needs to be taken and into a dictionary and an adjaceny matrix
    for s in dataStartNode:
        starNode=str(int(s[0]))
    mapDictionary={}
    mapDictionary1 = {}
    mapDictionaryTruck2 = {}
    mapDictionaryTruck3 = {}
    #starNode = "1"
    nodeListDemand=np.array([starNode])
    toadd =np.array([])
    #declare first row of adjacencyMatrix
    for s in dataDemand:
        nodeListDemand=np.append(nodeListDemand,[s._data])

    adjacencyMatrix=np.array([nodeListDemand])
    adjacencyMatrix1 = np.array([nodeListDemand])
    adjacencyMatrixTruck2 = np.array([nodeListDemand])
    adjacencyMatrixTruck3 = np.array([nodeListDemand])
    toadd=np.empty([1,nodeListDemand.size])
    toadd1 = np.empty([1, nodeListDemand.size])
    toaddTruck2 = np.empty([1, nodeListDemand.size])
    toaddTruck3 = np.empty([1, nodeListDemand.size])
    #for every demand node loop you create an adjacency matrix
    for idx in range(nodeListDemand.size):
        starNode=str(nodeListDemand[idx])
        previous_nodes, shortest_path = dijkstra_algorithm(graph=graphDamage, start_node=starNode)
        previous_nodes1, shortest_path1 = dijkstra_algorithm(graph=graphEmission, start_node=starNode)
        previous_nodes2, shortest_path2 = dijkstra_algorithm(graph=graphEmissionTruck2, start_node=starNode)
        previous_nodes3, shortest_path3 = dijkstra_algorithm(graph=graphEmissionTruck3, start_node=starNode)
        for idx2 in range(nodeListDemand.size):
            if idx==idx2:
                #put inf because node to itself is infinity
                toadd[0][idx2] =100000000000000000
                toadd1[0][idx2] = 100000000000000000
                toaddTruck2[0][idx2] = 100000000000000000
                toaddTruck3[0][idx2] = 100000000000000000
            else:
                #startNode = str(int(nodeListDemand[idx]))
                endNode = str(int(nodeListDemand[idx2]))
                pathResult =print_result(previous_nodes, shortest_path, start_node=starNode, target_node=endNode)
                pathResult1 = print_result(previous_nodes1, shortest_path1, start_node=starNode, target_node=endNode)
                pathResult2 = print_result(previous_nodes2, shortest_path2, start_node=starNode, target_node=endNode)
                pathResult3 = print_result(previous_nodes3, shortest_path3, start_node=starNode, target_node=endNode)
                mapDictionary["{},{}".format(starNode,endNode)]=pathResult
                mapDictionary1["{},{}".format(starNode, endNode)] = pathResult1
                mapDictionaryTruck2["{},{}".format(starNode, endNode)] = pathResult2
                mapDictionaryTruck3["{},{}".format(starNode, endNode)] = pathResult3
                toadd[0][idx2]=float(shortest_path[endNode])
                toadd1[0][idx2] = float(shortest_path1[endNode])
                toaddTruck2[0][idx2] = float(shortest_path2[endNode])
                toaddTruck3[0][idx2] = float(shortest_path3[endNode])
        adjacencyMatrix=np.append(adjacencyMatrix,toadd,axis=0)
        adjacencyMatrix1 = np.append(adjacencyMatrix1, toadd1, axis=0)
        adjacencyMatrixTruck2 = np.append(adjacencyMatrixTruck2, toadd1, axis=0)
        adjacencyMatrixTruck3 = np.append(adjacencyMatrixTruck3, toadd1, axis=0)
    #save the dictionary and the matrix
    dfAdj = pd.DataFrame(adjacencyMatrix)
    dfAdj = dfAdj.astype(float)
    dfMapDict = pd.DataFrame.from_dict(mapDictionary, orient='index')
    dfAdj.to_sql('adjMatrixDamages', con=db.engine, if_exists='replace', index_label='id')
    dfMapDict.to_sql('MapDictionaryDamages',con=db.engine,if_exists='replace', index_label='id')
    dfAdj = pd.DataFrame(adjacencyMatrix1)
    dfAdj = dfAdj.astype(float)
    dfMapDict = pd.DataFrame.from_dict(mapDictionary1, orient='index')
    dfAdj.to_sql('adjMatrixEmissions', con=db.engine, if_exists='replace', index_label='id')
    dfMapDict.to_sql('MapDictionaryEmissions', con=db.engine, if_exists='replace', index_label='id')
    dfAdj = pd.DataFrame(adjacencyMatrixTruck2)
    dfAdj = dfAdj.astype(float)
    dfMapDict = pd.DataFrame.from_dict(mapDictionaryTruck2, orient='index')
    dfAdj.to_sql('adjMatrixEmissionsTruckType2', con=db.engine, if_exists='replace', index_label='id')
    dfMapDict.to_sql('MapDictionaryEmissionsTruckType2', con=db.engine, if_exists='replace', index_label='id')
    dfAdj = pd.DataFrame(adjacencyMatrixTruck3)
    dfAdj = dfAdj.astype(float)
    dfMapDict = pd.DataFrame.from_dict(mapDictionaryTruck3, orient='index')
    dfAdj.to_sql('adjMatrixEmissionsTruckType3', con=db.engine, if_exists='replace', index_label='id')
    dfMapDict.to_sql('MapDictionaryEmissionsTruckType3', con=db.engine, if_exists='replace', index_label='id')
    return "completed"

#this function makes an adjacency matrix from a sql query output
#it returns the dictionary containg the adjacency matrix
def make_adjMatrix(dataadjacencyMatrix):
    skip = True
    fillRow1 = True
    addRow = []
    insert2D = 1
    adjacencyMatrixDamage = [[]]
    for s in dataadjacencyMatrix:
        if not skip:
            # get from col 1 to the end of the row and add the row underneath
            if fillRow1:
                for eachs in s[1:]:
                    addRow = np.append(addRow, eachs)
                adjacencyMatrixDamage.insert(0, addRow)
                fillRow1 = False
                addRow = []
            else:
                for eachs in s[1:]:
                    addRow = np.append(addRow, eachs)
                adjacencyMatrixDamage.insert(insert2D, addRow)
                addRow = []
                insert2D = insert2D + 1
        else:
            skip = False
    return adjacencyMatrixDamage

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)


