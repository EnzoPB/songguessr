from jinja2.lexer import describe_token
from flask import Blueprint, request, abort, jsonify
import requests

search_source_endpoint = Blueprint('search_source_endpoint', __name__)

@search_source_endpoint.route('/search_source')
def index():
    query = request.args.get('q')
    if not query:
        abort(400, description='Missing parameter q')
    
    results = []

    req = requests.get(f'https://api.deezer.com/search/artist?q={query}&limit=10')
    if not req.ok or 'error' in req.json():
        abort(500, description=f'Could not search artists: {req.text}')

    results.extend([
        {
            'name': a['name'],
            'id': a['id'],
            'type': 'artist'
        } for a in req.json()['data']
    ])

    req = requests.get(f'https://api.deezer.com/search/playlist?q={query}&limit=10')
    if not req.ok or 'error' in req.json():
        abort(500, description=f'Could not search playlists: {req.text}')
    results.extend([
        {
            'name': f'{p['title']} ({p['nb_tracks']} songs)',
            'id': p['id'],
            'type': 'playlist'
        } for p in req.json()['data']
    ])

    return jsonify(results)

