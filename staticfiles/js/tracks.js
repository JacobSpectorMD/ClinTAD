import { csrftoken } from './utilities.js';


// window.onload = function(){
//     initialize_tracks(tracks);
// };


$(document).on('click', '.toggle', function(){
    var toggle = $(this).parent();
    var row = $(toggle).parent();
    var input = this.querySelector('input');
    if ($(this).hasClass('off')) {var active = false}
    else {var active = true}

    // Uncheck all other TAD tracks, because only one is needed
    if ($(row).parent().attr('id') == 'TAD' && active){
        var tad_div = document.querySelector('#TAD')
        var tad_toggles = tad_div.querySelectorAll('.toggle');
        for (var i = 0; i < tad_toggles.length; i++){
            console.log(tad_toggles[i]);
            if (tad_toggles[i]!=this){
                var input2 = tad_toggles[i].firstChild;
                $(input2).bootstrapToggle('off');
            };
        }
    }

    if (!$(input).hasClass('default')){
        var ut_id = input.dataset.ut_id;
        var color = $(row).find('.color-picker').val();

        $.ajax({
            type: 'POST',
            url: '/user/edit_track/',
            headers: {'X-CSRFToken': csrftoken},
            data: {'ut_id': ut_id, 'color': color, 'active': active},
            success: function(data){}
        });
    }
})

function add_track(track){
    const trackDisplay = {'tad': 'TAD', 'cnv': 'CNV', 'enhancer': 'Enhancer', 'other': 'Other'};

    $('#my-tracks-tbody').append(
    `<tr class="mdc-data-table__row">
    <td class="mdc-data-table__cell use-track-cell">
        <div class="mdc-touch-target-wrapper">
          <div class="mdc-checkbox mdc-checkbox--touch">
            <input type="checkbox"
                     class="mdc-checkbox__native-control"
                     id="checkbox-1"/>
            <div class="mdc-checkbox__background">
              <svg class="mdc-checkbox__checkmark"
                     viewBox="0 0 24 24">
                  <path class="mdc-checkbox__checkmark-path"
                        fill="none"
                        d="M1.73,12.91 8.1,19.28 22.79,4.59"/>
              </svg>
              <div class="mdc-checkbox__mixedmark"></div>
            </div>
            <div class="mdc-checkbox__ripple"></div>
          </div>
        </div>
    </td>
    <td class="mdc-data-table__cell label-cell">${track.label}</td>
    <td class="mdc-data-table__cell user-cell">${trackDisplay[track.track_type]}</td>
    <td class="mdc-data-table__cell build-cell">${track.build}</td>
    <td class="mdc-data-table__cell description-cell">${track.details}</td>
</tr>`)
    
}

