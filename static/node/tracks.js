import {MDCSelect} from "@material/select";
import {MDCTabBar} from '@material/tab-bar';
import {MDCTextField} from "@material/textfield";
import {MDCDialog} from '@material/dialog';
import {csrftoken, initializeModal} from "../js/utilities.js";
import {Table} from "./table";
import {clearFields, showSnackbarError, snackbar} from "./base.js";

const buildSelect = new MDCSelect(document.querySelector('#build-select'));
const trackTypeSelect = new MDCSelect(document.querySelector('#track-type-select'));
const nameField = new MDCTextField(document.querySelector('#track-name-field'));
const authorLastNameField = new MDCTextField(document.querySelector('#author-last-name-field'));
const pubmedIdField = new MDCTextField(document.querySelector('#pubmed-id-field'));
const articleNameField = new MDCTextField(document.querySelector('#article-name-field'));

const dialog = new MDCDialog(document.querySelector('#track-dialog'));
const detailsField = new MDCTextField(document.querySelector('#details-field'));
const filterField = new MDCTextField(document.querySelector('#filter-field'));
const publicFilterField = new MDCTextField(document.querySelector('#public-filter-field'));


let table;
let publicTracksTable;

$(document).ready(function () {
    tracks.forEach(function (t) {
        t.use_track = get_checkbox(t);
        t.delete = get_delete(t)
    })
    table = new Table('my-tracks-table', tracks, filterField);

    publicTracks.forEach(function (publicTrack) {
        publicTrack.add_track_button = get_add_track_button(publicTrack);
    })
    publicTracksTable = new Table('public-tracks-table', publicTracks, publicFilterField);
    fade_public_tracks();
    allow_one_build();
})


// Switch between My Tracks and Public Tracks when the tabs are clicked
$(document).on('click', '#public-tracks-button', function () {
    $('#my-tracks-div, #create-track-div').css('display', 'none');
    $('#public-tracks-div').css('display', 'table');
    $('#public-filter-field').css('display', 'inline-flex');
    $('#filter-field').css('display', 'none');
})

$(document).on('click', '#my-tracks-button', function () {
    $('#public-tracks-div, #create-track-div').css('display', 'none');
    $('#my-tracks-div').css('display', 'table');
    $('#public-filter-field').css('display', 'none');
    $('#filter-field').css('display', 'inline-flex');
})

$(document).on('click', '#create-track-button', function () {
    $('#public-tracks-div, #my-tracks-div').css('display', 'none');
    $('#create-track-div').css('display', 'flex');
    $('#public-filter-field, #filter-field').css('display', 'none');
})

function get_delete(track) {
    const button = `
    <button type="button" data-user-track-id="${track.id}" class="red delete-track-button mdc-button mdc-button--touch mdc-button--raised">
        <div class="mdc-button__ripple"></div>
        <div class="mdc-button__label">Delete</div>
        <div class="mdc-button__touch"></div>
    </button>`
    return button;
}

// Delete button is pressed --> delete track or remove it
$(document).on('click', '.delete-track-button', function() {
    const button = this;
    const userTrackId = $(this).data('user-track-id');

    $.ajax({
        type: 'GET',
        url: '/user/delete_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'userTrackId': userTrackId},
        success: function (response) {
            allow_one_build();
            $(button).closest('.mdc-data-table__row').remove();
        },
    });
})


function get_checkbox(track) {
    let checked = "";
    if (track.active) {
        checked = "checked"
    }

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
$('#filter-input').on('input keydown', function () {
    table.add_filter(filterField.value);
});

// Filter the table by the entered term
$('#public-filter-input').on('input keydown', function () {
    publicTracksTable.add_filter(publicFilterField.value);
});

const tabBar = new MDCTabBar(document.querySelector('.mdc-tab-bar'));
tabBar.focusOnActivate = false;

$(document).on('click', '#submit-track-button', function () {
    submit_track();
})

$("#id_uploaded_file[type=file]").on('change', function () {
    $('#uploaded-file-name').html(this.files[0].name);
});

function submit_track() {
    const file = document.getElementById('id_uploaded_file').files[0];
    let data = new FormData();
    data.append('build', buildSelect.value);
    data.append('author_last_name', authorLastNameField.value);
    data.append('pubmed_id', pubmedIdField.value);
    data.append('article_name', articleNameField.value);
    data.append('details', detailsField.value);
    data.append('file', file);
    data.append('label', nameField.value);
    data.append('trackType', trackTypeSelect.value);

    const fieldsValid = checkValidity(buildSelect, nameField, trackTypeSelect);

    snackbar.setTitle('Processing');
    snackbar.setText('Your track is being processed, this may take a minute.');
    snackbar.timeoutMs = 5000;
    snackbar.open();

    clearFields(buildSelect, authorLastNameField, pubmedIdField, articleNameField, detailsField, nameField, trackTypeSelect);
    $('#uploaded-file-name').html('Click to upload file');

    $.ajax({
        type: 'POST',
        url: '/user/new_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: data,
        success: function (response) {
            console.log(response, response.label)
            snackbar.setTitle('Track Submitted');
            snackbar.setText(
                `Your track (${response.label}) has been added to the database. 
                Please go to your track tab to see your new track!`
            );
            snackbar.timeoutMs = 5000;
            snackbar.open();
        },
        error: function (jqXHR, textStatus, errorThrown) {
          showSnackbarError(jqXHR, textStatus, errorThrown);
        },
        cache: false,
        contentType: false,
        processData: false
    });
}



function checkValidity () {
    let valid = true;
    for (var i=0; i < arguments.length; i ++){
        let field = arguments[i];
        if (!field.valid) { valid = false}
    }
    return valid;
}

// When a track is checked by the user
$(document).on('click', '.use-track-div', function () {
    const item = $(this).closest('tr').data('item');
    const nowChecked = $(this).find('input').is(':checked')
    item.active = nowChecked;
    console.log(item);
    if (item.track_type == 'tad') {
        allow_one_build(item);
    }

    $.ajax({
        type: 'POST',
        url: '/user/update_user_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'user_track_id': item.ut_id, 'active': nowChecked},
        success: function (response) {},
    });
})


// If the user selects a TAD track, unselect and decrease opacity of any tracks that do not have the same genome build.
// The coordinates of different builds are not compatible, so only tracks from one build should be displayed at a time.
function allow_one_build(track = null) {

    // If the tad track (item) is not passed in, get the active TAD track
    if (!track) {
        track = table.items.find(function (item) {
            if (item.track_type == 'tad' && item.active == true) {
                return true
            } else {
                return false
            }
        })
    }

    if (track) {
        table.items.forEach(function (item) {

            // If a TAD track is passed, set tracks of other builds as inactive and disabled
            if (track.build != item.build) {
                item.active = false;
                // Uncheck rows from different builds
                $(item.row).find('input').prop('checked', false);

                // Disable non-TAD tracks from different builds
                if (item.track_type != 'tad') {
                    $(item.row).find('input').prop('disabled', true);
                    $(item.row).find('.mdc-data-table__cell:not(.delete)').css('opacity', 0.5);
                }
            } else {
                // If the build is the same as the TAD track, enable them
                $(item.row).find('input').prop('disabled', false);
                $(item.row).find('.mdc-data-table__cell').css('opacity', 1);
            }

            if (track.active && item.track_type == 'tad' && item != track) {
                // Only one TAD track is active at a time
                item.active = false;
                $(item.row).find('input').prop('checked', false);
            }
        })
    }


    if (!track || track.active == false) {
        table.items.forEach(function (item) {
            $(item.row).find('input').prop('disabled', false);
            $(item.row).css('opacity', 1);
        })
    }
}

$(document).on('click', '.add-track-button', function () {
    const publicTrack = $(this).closest('tr').data('item');
    console.log(publicTrack);
    publicTrack.already_added = true;
    publicTrack.add_track_button = get_add_track_button(publicTrack);
    publicTracksTable.display_items();

    $.ajax({
        type: 'POST',
        url: '/user/add_track/',
        headers: {'X-CSRFToken': csrftoken},
        data: {'id': publicTrack.id},
        success: function (item) {
            item.use_track = get_checkbox(item);
            item.delete = get_delete(item);
            table.items.push(item);
            table.display_items();
        },
    });
})

// For public tracks that the user already has in their own tracks, decrease the opacity and change the button text to
// "added"
function fade_public_tracks() {
    const my_track_ids = table.items.map(item => item.track_id);

    publicTracksTable.items.forEach(function (item) {
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

// Show more info about the track when it is clicked
$(document).on('click', '.mdc-data-table__row', function(e){
    // Don't show info when the user clicks the checkbox or delete button
    if ($(e.target).is('.use_track, .delete, input, button') || $(e.target).parents('button').length > 0) { return }

    let clickedTrack = this;
    if (!$(this).hasClass('.mdc-data-table__row')) {
        clickedTrack = $(this).closest('.mdc-data-table__row');
    }

    let searchTracks = tracks;
    if ( $(this).parents('#public-tracks-table').length > 0 ) {
        searchTracks = publicTracks;
    }
    const trackId = $(clickedTrack).data('id');
    const foundTrack = searchTracks.find(x => x.id == trackId);
    console.log(foundTrack);
    $('#track-label').html(foundTrack.label);
    $('#track-type').html(foundTrack.track_type);
    $('#track-build').html(foundTrack.build);
    $('#track-creator').html(foundTrack.creator);
    $('#track-details').html(foundTrack.details);
    $('#track-author').html(foundTrack.author_last_name);
    $('#track-year').html(foundTrack.year || '');
    $('#track-article').html(foundTrack.article_name);

    if (foundTrack.pubmed_id != '' && foundTrack.pubmed_id) {
        const pubmedLink = `https://pubmed.ncbi.nlm.nih.gov/${foundTrack.pubmed_id}/`
        $('#track-pubmed').html(`<a href='${pubmedLink}' target='blank'>${pubmedLink}</a>`);
    } else {
        $('#track-pubmed').html('');
    }
    dialog.open();
})