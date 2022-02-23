import {MDCSelect} from '@material/select';
import {MDCTextField} from '@material/textfield';

import { addHpoFunctions } from "./utilities";

const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));

const elements = addHpoFunctions();
const select = elements.select;
const phenotypesField = elements.phenotypesField;

$(document).ready(function () {
    if (coordinates) {
        coordinatesField.value = coordinates;
    }
    
    if (phenotypes !== '') {
        phenotypesField.value = phenotypes;
    }
})

$(document).on('click', '#track-labels-button', function() {
    $('.track-label').toggleClass('hidden');
})

$(document).on('click', '#statistics-button', function() {
    if (!coordinates || !phenotypes) { return }
    var url = `/single/statistics/?coordinates=${coordinates}&phenotypes=${phenotypes}`;
    window.open(url, "_blank");
})

