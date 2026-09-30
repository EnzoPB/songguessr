let songs = [];

$(function() {
    $('#form-settings').on('submit', function (e) {
        e.preventDefault();

        Swal.fire({
            title: 'Loading...',
            theme: 'dark',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false
        });
        Swal.showLoading();
        let source = $('#input-playlist').val();
        let songs_count = $('#input-songs-count').val();
        let difficulty = $('#input-difficulty').val();
        fetch(`/create_game?source=${source}&songs_count=${songs_count}&difficulty=${difficulty}`)
            .then(data => data.json())
            .then(data => {
                console.log(data);
                songs = data.tracks;
                $('#game-title').text(data.title);
                $('#settings-screen').hide();
                $('#game-screen').show();
                round = -1;
                next_round();
                Swal.close();
            });
    });
});


// search
let source_search_timeout = null;
let last_source_search_query = '';

function trigger_source_search() {
    if (source_search_timeout != null) {
        clearTimeout(source_search_timeout);
    }
    let query = $('#input-source-search').val().trim();
    if (query == '' || query == last_source_search_query) {
        return;
    }
    fetch('/search_source?q=' + encodeURIComponent(query))
        .then(data => data.json())
        .then(suggestions => {
            last_source_search_query = query;
            $('#source-search-suggestions').attr('disabled', false);
            $('#source-search-suggestions').html('');
            if (suggestions.length == 0) {
                $('#source-search-suggestions').attr('disabled', true);
                $('#source-search-suggestions').html('<option>Nothing found</option>');
            }
            for (let item of suggestions) {
                let el = $('<option>');
                el.text(`${item.type}: ${item.name}`);
                el.val(`https://www.deezer.com/${item.type}/${item.id}`);
                $('#source-search-suggestions').append(el);
            }
        });
}

$(function() {
    $('#input-source-search').on('keyup', function (event) {
        if (event.key == 'Enter') {
            trigger_source_search();
        }
    });

    $('#input-source-search').on('input', function () {
        if (source_search_timeout != null) {
            clearTimeout(source_search_timeout);
        }
        source_search_timeout = setTimeout(trigger_source_search, 1500);
    });

    $('#source-search-suggestions').on('change', function () {
        $('#input-playlist').val($('#source-search-suggestions').val());
        $('#source-search-suggestions').html('');
        $('#input-source-search').val('');
    });
});