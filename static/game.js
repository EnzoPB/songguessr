
const round_stages = [0.5, 2, 5, 15, 30];
let round = 0;
let round_stage = 0;
let player = null;
let points = 0;


$(function() {
    player = $('#player');
});

// basic game functions and states
function next_round() {
    $('#round-end-screen').hide();
    if (round == songs.length - 1) {
        $('#game-end-screen').show();
        player[0].pause();
        return;
    }
    round++;
    let song = songs[round];
    round_stage = 0;
    $('#btn-skip').show();
    $('#btn-give-up').hide();
    $('#stage').val(round_stages[0]);
    $('#progress').val(0);
    $('#points').text(0);
    player[0].pause();
    console.log(`round ${round}, song:`, song);
    player.attr('src', song.preview_url);
    $('#game-screen').show();
}

function next_stage() {
    if (round_stage == round_stages.length - 1) {
        show_answer();
        return;
    }
    round_stage++;
    $('#stage').val(round_stages[round_stage]);
    if (round_stage == round_stages.length - 1) {
        $('#btn-skip').hide();
        $('#btn-give-up').show();
    }
}

function show_answer() {
    $('#song-image').attr('src', songs[round].cover_url);
    $('#song-title').text(songs[round].title);
    $('#song-artist').text(songs[round].artist);
    $('#total-points').text(points);
    $('#round-end-screen').show();
    $('#game-screen').hide();
    player[0].currentTime = 0;
}

$(function() {
    $('#btn-play').on('click', function () {
        player[0].currentTime = 0;
        player[0].play();
    });
    $('#btn-skip').on('click', next_stage);
    $('#btn-give-up').on('click', show_answer);
    $('#btn-next-round').on('click', next_round);
});


// search
let track_search_timeout = null;
let last_track_search_query = '';
let guess_history = [];

function trigger_track_search() {
    if (track_search_timeout != null) {
        clearTimeout(track_search_timeout);
    }
    let query = $('#input-track-search').val().trim();
    if (query == '' || query == last_track_search_query) {
        return;
    }
    api_request('/search_track?q=' + encodeURIComponent(query))
        .then(suggestions => {
            last_track_search_query = query;
            $('#track-search-suggestions').attr('disabled', false);
            $('#track-search-suggestions').html('');
            if (suggestions.length == 0) {
                $('#track-search-suggestions').attr('disabled', true);
                $('#track-search-suggestions').html('<option>Nothing found</option>');
            }
            for (let track of suggestions) {
                let el = $('<option>');
                el.text(track);
                if (guess_history.includes(track)) {
                    el.attr('disabled', true);
                }
                $('#track-search-suggestions').append(el);
            }
        });
}

$(function() {
    $('#input-track-search').on('keyup', function (event) {
        if (event.key == 'Enter') {
            trigger_track_search();
        }
    });

    $('#input-track-search').on('input', function () {
        if (track_search_timeout != null) {
            clearTimeout(track_search_timeout);
        }
        track_search_timeout = setTimeout(trigger_track_search, 1500);
    });

    $('#track-search-suggestions').on('change', function () {
        let guess = $('#track-search-suggestions').val();
        guess_history.push(guess);
        if (songs[round].title + ' - ' + songs[round].artist == guess) {
            let round_point = (round_stages.length - round_stage) ** 2;
            points += round_point;
            $('#points').text(round_point);
            show_answer();
        } else {
            next_stage();
        }
        $('#track-search-suggestions').html('');
        $('#input-track-search').val('');
    });
});

$(function() {
    setInterval(function () {
        if (!player.is(':visible') && !player[0].paused) {
            $('#progress').val(player[0].currentTime);
            if (player[0].currentTime >= round_stages[round_stage]) {
                player[0].pause();
                player[0].currentTime = round_stages[round_stage];
            }
        }
    }, 50);
});
