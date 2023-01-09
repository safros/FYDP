#main.py
#https://gist.github.com/dasdachs/69c42dfcfbf2107399323a4c86cdb791
import os
import csv
from io import TextIOWrapper
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
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

@app.route("/viewEntries")
def viewEntries ():
    list = db.engine.execute("SELECT * FROM cost").fetchall()
    return render_template('dbview.html',list=list)

@app.route("/upload_csv")
def view ():
    #view the table/csv uploaded
    #run model on the data
    #call dijstra's algorithm on the data to create the distance matrix
    #call heuristic
    #running the opti on Gurobi
    return render_template('view.html')

def heuristic():
    return "run heuristic"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)


