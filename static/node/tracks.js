import {MDCDataTable} from '@material/data-table';
import {MDCSelect} from "@material/select";
import {MDCTextField} from "@material/textfield";

import { csrftoken } from "../js/utilities.js";


const buildSelect = new MDCSelect(document.querySelector('#build-select'));
const trackTypeSelect = new MDCSelect(document.querySelector('#track-type-select'));
const nameField = new MDCTextField(document.querySelector('#track-name-field'));
const detailsField = new MDCTextField(document.querySelector('#details-field'));

$(document).on('click', '#submit-track-button', function() {
    console.log('click')
    submit_track();
})

function submit_track () {
    console.log('submit')
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

// Expand the description cells for tracks when they are clicked
$(document).on('click', '.mdc-data-table__row', function(){
    if ($(this).hasClass('wrap')) {
        $(this).removeClass('wrap').find('td').css('white-space', 'nowrap');
    } else {
        $(this).addClass('wrap').find('td').css('white-space', 'initial');
    }
})