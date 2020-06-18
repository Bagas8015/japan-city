from flask import Flask, request, g, render_template
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from flask_restful import Resource, Api

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')
