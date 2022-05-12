import {MDCTextField} from "@material/textfield";

import {Table} from './table.js';
import {initializeModal} from '../js/utilities';

function get_link_html(c){
    const link = `/single/?build=${c.build}&coordinates=${c.coordinates}&phenotypes=${c.phenotypes}`

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
