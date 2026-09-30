from jinja2.lexer import describe_token
from flask import Blueprint, request, abort, jsonify
import requests

search_track_endpoint = Blueprint('search_track_endpoint', __name__)

@search_track_endpoint.route('/search_track')
def index():
    query = request.args.get('q')
    if not query:
        abort(400, description='Missing parameter q')
    
    req = requests.get(f'https://api.deezer.com/search/track/?q={query}')
    req.raise_for_status()
    if 'error' in req.json():
        abort(500, description=f'Could not search: {req.text}')

    tracks = req.json()['data']

    return jsonify([f'{t['title']} - {t['artist']['name']}' for t in tracks])

