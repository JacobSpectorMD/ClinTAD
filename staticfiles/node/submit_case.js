import {MDCSelect} from "@material/select";
import {MDCTextField} from "@material/textfield";

import {addHpoFunctions} from "./utilities";
import {csrftoken} from "../js/utilities";


const elements = addHpoFunctions();
const buildSelect = new MDCSelect(document.querySelector('#build-select'));
const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));
const pubmedField = new MDCTextField(document.querySelector('#pubmed-field'));
const phenotypesField = elements.phenotypesField;
const commentsField = new MDCTextField(document.querySelector('#comments-field'));

$(document).on('click', '#submit-data-button', function () {
    const build = buildSelect.value;
    const coordinates = coordinatesField.value;
    const pubmeds = pubmedField.value;
    const phenotypes = phenotypesField.value;
    const comments = commentsField.value;

    const data = {
        'build': build,
        'coordinates': coordinates,
        'pubmeds': pubmeds,
        'phenotypes': phenotypes,
        'comments': comments
    };

    $.ajax({
        type: 'POST',
        url: '/single/submit_case/',
        headers: {'X-CSRFToken': csrftoken},
        data: data,
        success: function (response) {
            window.location.href = '/single/submitted_case/';
        },
    });
})

