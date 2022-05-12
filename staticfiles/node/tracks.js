import {MDCSelect} from "@material/select";
import {MDCTabBar} from '@material/tab-bar';
import {MDCTextField} from "@material/textfield";

import {csrftoken, initializeModal} from "../js/utilities.js";
import {Table} from "./table";


const buildSelect = new MDCSelect(document.querySelector('#build-select'));
const trackTypeSelect = new MDCSelect(document.querySelector('#track-type-select'));
const nameField = new MDCTextField(document.querySelector('#track-name-field'));
const detailsField = new MDCTextField(document.querySelector('#details-field'));
const filterField = new MDCTextField(document.querySelector('#filter-field'));
const publicFilterField = new MDCTextField(document.querySelector('#public-filter-field'));


let table;
let publicTracksTable;

$(document).ready(function(){
    tracks.forEach(function (t){
        t.use_track = get_checkbox(t);
    })
    table = new Table('my-tracks-table', tracks, filterField);

    publicTracks.forEach(function(publicTrack){
        publicTrack.add_track_button = get_add_track_button(publicTrack);
    })
    publicTracksTable = new Table('public-tracks-table', publicTracks, publicFilterField);
    fade_public_tracks();
    allow_one_build();
})



// Switch between My Tracks and Public Tracks when the tabs are clicked
$(document).on('click', '#public-tracks-button', function(){
    $('#public-tracks-div').css('display', 'table');
    $('#my-tracks-div').css('display', 'none');
    $('#public-filter-field').css('display', 'inline-flex');
    $('#filter-field').css('display', 'none');
})

$(document).on('click', '#my-tracks-button', function(){
    $('#public-tracks-div').css('display', 'none');
    $('#my-tracks-div').css('display', 'table');
    $('#public-filter-field').css('display', 'none');
    $('#filter-field').css('display', 'inline-flex');
})

function get_checkbox(track) {
    let checked = "";
    if (track.active) {checked = "checked"}

     const use_track_checkbox = ` 
        <div class="mdc-touch-target-wrapper use-track-div">
          <div class="mdc-checkbox mdc-checkbox--touch">
            <input type="checkbox" class="mdc-checkbox__native-control" ${checked}/>
            <div class="mdc-checkbox__background">
              <svg class="mdc-checkbox__checkmark" viewBox="0 0 24 24">
                <path class="mdc-checkbox__checkmark-path" fill="none" d="M1.73,12.91 8.1,19.28 22.79,4.59"/>
              </svg>
              <div class="mdc-checkbox__mixedmark"></div>
            </div>
            <div class="mdc-checkbox__ripple"></div>
          </div>
        </div>
    `;

     return use_track_checkbox
}

function get_add_track_button(track) {
    const disabled = track.already_added ? 'disabled' : '';
    const text = track.already_added ? 'Added' : 'Add Track'

    const button = `
    <button type="button" data-track-id="${track.id}" ${disabled} class="add-track-button mdc-button mdc-button--touch mdc-button--raised">
        <div className="mdc-button__ripple"></div>
        <div className="mdc-button__label">${text}</div>
        <div className="mdc-button__touch"></div>
    </button>`
    return button;
}


// Filter the table by the entered term
$('#filter-input').on('input keydown', function(){
    table.add_filter(filterField.value);
});

// Filter the table by the entered term
$('#public-filter-input').on('input keydown', function(){
    publicTracksTable.add_filter(publicFilterField.value);
});

const tabBar = new MDCTabBar(document.querySelector('.mdc-tab-bar'));
tabBar.focusOnActivate = false;

$(document).on('click', '#submit-track-button', function() {
    submit_track();
})

function submit_track () {
    const file = document.getElementById('id_uploaded_file').files[0];
    let data = new FormData();
    data.append('build', buildSelect.value);
    data.append('details', detailsField.value);
    data.append('file', file);
    data.append('label', nameField.value);
    data.append('trackType', trackTypeSelect.value);

    $.ajax({
        type: 'POST',
        url: '/user/new_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: data,
        success: function(response) {
            console.log(response);
        },
        cache: false,
        contentType: false,
        processData: false
    });
}


$(document).on('click', '.use-track-div', function(){
    const item = $(this).closest('tr').data('item');
    const nowChecked = $(this).find('input').is(':checked')
    item.active = nowChecked;

    if (item.track_type == 'tad'){
        allow_one_build(item);
    }

    $.ajax({
        type: 'POST',
        url: '/user/update_user_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'user_track_id': item.ut_id, 'active': nowChecked},
        success: function(response) {

        },
    });
})


// If the user selects a TAD track, unselect and decrease opacity of any tracks that do not have the same genome build.
// The coordinates of different builds are not compatible, so only tracks from one build should be displayed at a time.
function allow_one_build(track=null) {

    // If the tad track (item) is not passed in, get the active TAD track
    if (!track) {
         track = table.items.find(function(item){
            if (item.track_type == 'tad' && item.active == true) {
                return true
            } else {
                return false
            }
        })
    }

    if (track) {
        table.items.forEach(function(item){

            // If a TAD track is passed, set tracks of other builds as inactive and disabled
            if (track.build != item.build) {
                item.active = false;
                // Uncheck rows from different builds
                $(item.row).find('input').prop('checked', false);

                // Disable non-TAD tracks from different builds
                if (item.track_type != 'tad') {
                    $(item.row).find('input').prop('disabled', true);
                    $(item.row).css('opacity', 0.5);
                }
            } else {
                // If the build is the same as the TAD track, enable them
                $(item.row).find('input').prop('disabled', false);
                $(item.row).css('opacity', 1);
            }
        })
    }


    if (!track || track.active == false) {
        table.items.forEach(function(item){
            $(item.row).find('input').prop('disabled', false);
            $(item.row).css('opacity', 1);
        })
    }
}

$(document).on('click', '.add-track-button', function(){
    const item = $(this).closest('tr').data('item');

    $.ajax({
        type: 'POST',
        url: '/user/add_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'id': item.id},
        success: function(item) {
            console.log(item);
            item.use_track = get_checkbox(item);
            table.items.push(item);
            table.display_items();
        },
    });
})

// For public tracks that the user already has in their own tracks, decrease the opacity and change the button text to
// "added"
function fade_public_tracks () {
    const my_track_ids = table.items.map(item => item.track_id);

    publicTracksTable.items.forEach(function(item){
        if (my_track_ids.includes(item.id)) {
            item.already_added = true;
            item.add_track_button = get_add_track_button(item);
            $(item.row).find('.add-track-button').prop('disabled', true).html('Added');
        } else {
            item.already_added = false;
            item.add_track_button = get_add_track_button(item);
            $(item.row).find('.add-track-button').prop('disabled', false).html('Add Track');
        }
    })
}
