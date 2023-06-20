import {MDCTabBar} from '@material/tab-bar';
import {MDCCheckbox} from '@material/checkbox';
import {MDCDialog} from '@material/dialog';
import {MDCFormField} from '@material/form-field';
import {MDCSelect} from "@material/select";
import {MDCTextField} from "@material/textfield";

import {Table} from './table.js';
import {csrftoken, initializeModal} from '../js/utilities';
import {addHpoFunctions} from './utilities';
import {clearFields, showSnackbarError, snackbar} from "./base";

// Checkbox & fields
const checkbox = new MDCCheckbox(document.querySelector('.mdc-checkbox'));
const checkboxField = new MDCFormField(document.querySelector('#evidence-field'));

// Other fields
const buildSelect = new MDCSelect(document.querySelector('#build-select'));
const commentsField = new MDCTextField(document.querySelector('#comments-field'));
const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));
const phenotypesField = new MDCTextField(document.querySelector('#phenotypes-field'));
const pubmedIdField = new MDCTextField(document.querySelector('#pubmed-ids-field'));

// Tab bar at top of the card
const tabBar = new MDCTabBar(document.querySelector('.mdc-tab-bar'));
tabBar.focusOnActivate = false;

// Dialog with more info when case is clicked
const dialog = new MDCDialog(document.querySelector('#case-dialog'));


// Functionality for HPO search fields
addHpoFunctions();

function get_link_html(c){
    const link = `/single/example/?build=${c.build}&coordinates=${c.coordinates}&phenotypes=${c.phenotypes}`

    const html = `
    <button class="mdc-button mdc-button--icon-leading" onClick="window.open('${link}','_blank')">
        <span class="mdc-button__ripple"></span>
        <i class="material-icons mdc-button__icon" aria-hidden="true"
        >open_in_new</i
        >
        <span class="mdc-button__label">View</span>
    </button>`
    return html;
}

const filterField = new MDCTextField(document.querySelector('#filter-field'));

$(document).ready(function(){
    initializeModal('#about-button');

    cases.forEach(function(c){
        c.link = get_link_html(c);
    })
    const table = new Table('cases-table', cases, filterField);

    // Filter the table by the entered term
    $('#filter-input').on('input keydown', function(){
        table.add_filter(filterField.value);
    });
})


// Switch between My Tracks and Public Tracks when the tabs are clicked
$(document).on('click', '#case-list-button', function () {
    $('#create-case-div').css('display', 'none');
    $('#case-list-div').css('display', 'table');
})

$(document).on('click', '#create-case-button', function () {
    $('#case-list-div').css('display', 'none');
    $('#create-case-div').css('display', 'flex');
})

// On clicking the submit button
$(document).on('click', '#submit-data-button', function() {
    const build = buildSelect.value;
    const comments = commentsField.value;
    const coordinates = coordinatesField.value;
    const phenotypes = phenotypesField.value;
    const pubmeds = pubmedIdField.value;

    let evidence = '';
    $('input[type="checkbox"]').each(function() {
        if (this.checked) {
            evidence += $(this).data('value') + ', '
        }
    });
    if (evidence.includes(',')) {
        evidence = evidence.slice(0, -2)
    }

    snackbar.setTitle('Processing');
    snackbar.setText('Your case is being processed, this may take a minute.');
    snackbar.timeoutMs = 5000;
    snackbar.open();

    clearFields(buildSelect, commentsField, coordinatesField, checkboxField, phenotypesField, pubmedIdField);

    $.ajax({
        type: 'POST',
        url: '/single/submit_case/',
        headers: {'X-CSRFToken': csrftoken},
        data: {build, comments, coordinates, evidence, phenotypes, pubmeds},
        success: function (response) {
            clearFields(buildSelect, commentsField, coordinatesField, formField, phenotypesField, pubmedIdField);
            snackbar.setTitle('Case Submitted');
            snackbar.setText(`Your case has successfully been added to the database.`);
            snackbar.timeoutMs = 5000;
            snackbar.open();        },
        error: function (jqXHR, textStatus, errorThrown) {
          showSnackbarError(jqXHR, textStatus, errorThrown);
        },
    });

})

// Show more info about the track when it is clicked
$(document).on('click', '.mdc-data-table__row', function(e){
    // Don't open the case info when buttons are clicked in rows
    if ($(e.target).is('button') || $(e.target).parents('button').length > 0) { return }

    const caseId = $(this).data('id');
    const c = cases.find(x => x.id == caseId);
    console.log(c);

    $('#case-status').html(c.status);
    $('#case-build').html(c.build);
    $('#case-coordinates').html(c.coordinates);
    $('#case-phenotypes').html(c.phenotypes);
    $('#case-submitter').html(c.submitter);
    $('#case-evidence').html(c.evidence);
    $('#case-comments').html(c.comments);
    $('#case-pubmed').html(c.pubmed_ids);

    dialog.open();
})