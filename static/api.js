function error_modal(title, message) {
    Swal.fire({
        icon: 'error',
        title: title,
        text: message,
        theme: 'dark'
    });
}

function api_request(url) {
    return fetch(url)
        .then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                response.text().then(function(text) {
                    error_modal(response.statusText, text);
                })
            }
        })
        .catch(function(err) {
            error_modal('Unknown error', err);
        })
}