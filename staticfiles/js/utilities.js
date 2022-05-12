function getCookie (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export const csrftoken = getCookie('csrftoken');

export function initializeModal(button) {
    const modalId = '#'+$(button).data('modal-id');
    $(button).on('click', function(){
        if ($(modalId).css('display') == 'none' || $(modalId).css('display') == undefined) {
            $(modalId).css('display', 'flex');
        } else {
            $(modalId).css('display', 'none');
        }
    })

    $(modalId).on('click', function(){
        if ($(this).hasClass('modal')){
            $('.modal').css('display', 'none');
        }
    })

    $(modalId).find('.close').on('click', function() {
        $('.modal').css('display', 'none');
    })
}