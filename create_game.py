from flask import Blueprint, request, abort, jsonify
import random
import dataclasses

import source

create_game_endpoint = Blueprint('create_game_endpoint', __name__)

@create_game_endpoint.route('/create_game')
def index():
    source_link = request.args.get('source')
    songs_count_str = request.args.get('songs_count')
    difficulty_str = request.args.get('difficulty')

    if not source_link or not songs_count_str or not difficulty_str:
        abort(400, description='Missing parameter source, songs_count, or difficulty')

    try:
        songs_count = int(songs_count_str)
        difficulty = int(difficulty_str)
        assert songs_count in range(0, 16) and difficulty in range(0, 4)
    except (ValueError, AssertionError):
        abort(400, description='Bad parameter value')
        
    title, tracks = source.get(source_link)

    if difficulty != 0:
        tracks = sorted(tracks, key=lambda track: track.rank, reverse=True)
        difficulty_groups_size = len(tracks) // 3
        difficulty_groups = [tracks[i:i+difficulty_groups_size] for i in range(0, len(tracks), difficulty_groups_size)]

        print([sum([t.rank for t in g]) / len(g) for g in difficulty_groups if g])
        random.shuffle(difficulty_groups[difficulty - 1])
        game_tracks = difficulty_groups[difficulty - 1][:songs_count]
    else:
        random.shuffle(tracks)
        game_tracks = tracks[:songs_count]
    
    processed_tracks = []
    for track in game_tracks:
        if track.title is None:
            track.resolve()  # Get missing info from Deezer
        if track.preview_url != '':
            processed_tracks.append(track)
            
    game_tracks = processed_tracks

    return jsonify({
        'title': title,
        'tracks': [dataclasses.asdict(t) for t in game_tracks]
    })