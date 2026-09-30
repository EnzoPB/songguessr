import flask
import requests
import traceback
from werkzeug.exceptions import HTTPException
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

@app.errorhandler(Exception)
def handle_exception(error: Exception):
    if isinstance(error, HTTPException):  # normal server error (404, 400, etc)
        response = flask.make_response(f'{error.code} {error.name}: {error.description}', error.code)
    elif isinstance(error, requests.HTTPError) and error.response is not None:  # http client error (deezer/spotify api)
        response = flask.make_response(f'External API error {error.response.status_code}: {error.response.text}', error.response.status_code)
        traceback.print_exception(error)
    else:  # other error
        response = flask.make_response(str(error), 500)
        traceback.print_exception(error)
    response.mimetype = 'text/plain'
    return response

app.run(port=5000)