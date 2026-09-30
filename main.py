import flask
from create_game import create_game_endpoint
from search_track import search_track_endpoint
from search_source import search_source_endpoint

app = flask.Flask(__name__)
app.register_blueprint(create_game_endpoint)
app.register_blueprint(search_track_endpoint)
app.register_blueprint(search_source_endpoint)

@app.route('/')
def index():
    return flask.send_file('index.html')

@app.route('/static/<path:path>')
def static_index(path):
    return flask.send_from_directory('static', path)