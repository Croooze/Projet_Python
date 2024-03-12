from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/index/')
@app.route('/index/<name>')
def hello(name=None):
    return render_template('index.html', name=name)