#main.py
#https://gist.github.com/dasdachs/69c42dfcfbf2107399323a4c86cdb791
import os
import csv
from io import TextIOWrapper
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import numpy as np
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
        costData = pd.read_excel(csv_file, 'cost')
        distanceData = pd.read_excel(csv_file, 'distance')
        truckData = pd.read_excel(csv_file, 'truck')
        demandData = pd.read_excel(csv_file,'demand')
        #for row in csv_reader:
        #user = User(username=row[0], email=row[1])
        #db.session.add(user)
        #dataDB = DataForModel(cost=row[0])
        #db.session.add(dataDB)
        costData.to_sql('cost', con=db.engine, if_exists='replace')
        distanceData.to_sql('distance', con=db.engine, if_exists='replace', index_label='id')
        truckData.to_sql('truck', con=db.engine, if_exists='replace', index_label='id')
        demandData.to_sql('demand', con=db.engine, if_exists='replace', index_label='id')
        list = db.engine.execute("SELECT * FROM cost").fetchall()
        print(list)
        db.session.commit()
        return render_template('dbview.html',list=list)

    return render_template('index.html')

@app.route("/instructions")
def instructions():
    return render_template('instructions.html')

@app.route("/model")
def display():
    return render_template('model.html')

@app.route("/dbview")
def viewEntries ():
    list = db.engine.execute("SELECT * FROM cost").fetchall()
    return render_template('dbview.html',list=list)

@app.route("/run_model")
def runModel ():
    #run model on the data
    #call dijstra's algorithm on the data to create the distance matrix
    dijstra()
    #call heuristic
    anArray = heuristic()
    #running the opti on Gurobi

    #display a map of the final solution

    return render_template('runModel.html', listPrint = anArray)

def heuristic():
    truck_paths = {0: np.array([0]), 1: np.array([0]), 2: np.array([0]), 3: np.array([0])}
    truck_capacity = np.array(db.engine.execute("SELECT * FROM truck").fetchall())
    demand_Retailer = np.array(db.engine.execute("SELECT * FROM demand").fetchall())
    adjacencyMatrix = np.array(db.engine.execute("SELECT * FROM distance").fetchall())
    # cost $/km for ESAL damage based on vehicle
    esal_k = [0.1, 0.1, 0.05, 0.05]
    # cost of $/km for GHG damage based on vehicle
    ghg_k = [0, 0, 0.07334474, 0.07334474]

    # initialize
    remaining_Cust = np.array(db.engine.execute("SELECT * FROM demand").fetchall())
    remaining_Demand = np.array(db.engine.execute("SELECT * FROM demand").fetchall())
    remaining_truck_capacity = np.array(db.engine.execute("SELECT * FROM truck").fetchall())
    currLocation = 0
    numTruck = 0
    loadPerTruck = {0: np.array([]), 1: np.array([]), 2: np.array([]), 3: np.array([])}
    print("truck capacity: IS IT OK?")
    print(truck_capacity)
    return truck_capacity

def dijstra ():
    return "run shortest path alg"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)


