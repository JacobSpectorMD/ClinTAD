function getCookie(name) {
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
var csrftoken = getCookie('csrftoken');

function initialize_tracks(tracks){
    console.log(tracks);
    // Add all of the user's tracks to their section
    tracks.tracks.forEach(function(track){
        var row = document.createElement('div');
        row.setAttribute('class', 'track-row');
        row.setAttribute('data-ut-id', track.ut_id);

        // Toggle button
        var col = document.createElement('div');
        col.setAttribute('class', 'toggle-col');
        var check = track.active ? 'checked' : '';
        col.innerHTML = '<input type="checkbox" '+check+' class="track-toggle" data-toggle="toggle" data-on="Yes"'+
                        'data-off="No" data-ut_id="'+track.ut_id+'">';
        row.appendChild(col);

        // Label
        var col = document.createElement('div');
        col.setAttribute('class', 'label-col');
        col.innerHTML = track.label;
        row.appendChild(col);

        // Build
        var col = document.createElement('div');
        col.setAttribute('class', 'build-col');
        col.innerHTML = track.build;
        row.appendChild(col);

        // Color
        var col = document.createElement('div');
        col.setAttribute('class', 'color-col');
        if (track.track_type == 'TAD'){col.innerHTML = '';}
        else {col.innerHTML = '<input class="color-picker" type="color" value="'+track.color+'">';}
        row.appendChild(col);

        // Details
        var col = document.createElement('div');
        col.setAttribute('class', 'details-col');
        col.innerHTML = track.details;
        row.appendChild(col);

        // Delete button
        var col = document.createElement('div');
        col.setAttribute('class', 'delete-col');
        col.innerHTML = '<button>Delete</button>';
        row.appendChild(col);

        var table = document.getElementById(track.track_type);
        table.appendChild(row);
    })

    $('.track-toggle').bootstrapToggle();
    if (tracks.default_tads) {$('#tad-toggle').bootstrapToggle('on');}
    if (tracks.default_enhancers){$('#enhancer-toggle').bootstrapToggle('on');}

    // Turn off default enhancers when clicked
    $('#enhancer-toggle').change(function(){
        if ($('#enhancer-toggle').parent().hasClass('off')) {var active = false}
        else {var active = true}

        $.ajax({
            type: 'POST',
            url: '/user/default_enhancers/',
            headers: {'X-CSRFToken': csrftoken},
            data: {'active': active},
            success: function(data){}
        });
    })

    // Turn off default tads when clicked
    $('#tad-toggle').change(function(){
        if ($('#tad-toggle').parent().hasClass('off')) {var active = false}
        else {var active = true}

        $.ajax({
            type: 'POST',
            url: '/user/default_tads/',
            headers: {'X-CSRFToken': csrftoken},
            data: {'active': active},
            success: function(data){}
        });
    })

    color_listener();
}


$(document).on('click', '.delete-col button', function(){
    var button = this;
    var row = $(button).parent().parent();
    var ut_id = $(row).data('ut-id');
    $.ajax({
        type: 'POST',
        url: '/user/delete_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'ut_id': ut_id},
        success: function(data){
            row.remove();
        }
    });
})

function color_listener(){
    var colorPicker = document.getElementsByClassName('color-picker');

    for (var i = 0 ; i < colorPicker.length; i++) {
        colorPicker[i].addEventListener("input", color_input, false);
    }
}

$(document).on('click', '.toggle', function(){
    var toggle = $(this).parent();
    var row = $(toggle).parent();
    var input = this.querySelector('input');
    var ut_id = input.dataset.ut_id;

    var color = $(row).find('.color-picker').val();
    if ($(this).hasClass('off')) {var active = false}
    else {var active = true}

    // Uncheck all other TAD tracks, because only one is needed
    if ($(row).parent().attr('id') == 'TAD' && active){
        var tad_div = document.querySelector('#TAD')
        var tad_toggles = tad_div.querySelectorAll('.toggle');
        for (var i = 0; i < tad_toggles.length; i++){
            if (tad_toggles[i]!=this){
                var input2 = tad_toggles[i].firstChild;
                $(input2).bootstrapToggle('off');
            };
        }
    }

    $.ajax({
        type: 'POST',
        url: '/user/edit_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'ut_id': ut_id, 'color': color, 'active': active},
        success: function(data){}
    });
})

function color_input(event){
    var row = $(event.target).parent().parent();
    var color = event.target.value;
    event.target.setAttribute('value', event.target.value);

    var ut_id = $(row).data('ut-id');
    var toggle = $(row).find('.toggle');

    if ($(toggle).hasClass('off')) {var active = false}
    else {var active = true}

    $.ajax({
        type: 'POST',
        url: '/user/edit_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'ut_id': ut_id, 'color': color, 'active': active},
        success: function(data){}
    });
}

