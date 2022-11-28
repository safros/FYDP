#main.py
#https://gist.github.com/dasdachs/69c42dfcfbf2107399323a4c86cdb791
import csv
from io import TextIOWrapper
from flask import Flask, render_template, request, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db = SQLAlchemy(app)

@app.route("/", methods=('GET','POST'))

def index ():
    #def upload_csv():
        #if request.method == 'POST':
            #csv_file = request.files['file']
            #csv_file = TextIOWrapper(csv_file, encoding='utf-8')
            #csv_reader = csv.reader(csv_file, delimiter=',')
            #for row in csv_reader:
                #user = User(username=row[0], email=row[1])
                #db.session.add(user)
                #db.session.commit()
            #return redirect(url_for('upload_csv'))
    return render_template('index.html')

@app.route("/instructions")
def instructions():
    return render_template('instructions.html')

@app.route("/model")
def display():
    return render_template('model.html')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)


