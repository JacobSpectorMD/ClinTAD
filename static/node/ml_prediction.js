import {MDCTextField} from '@material/textfield';

import {csrftoken} from "../js/utilities";
import {draw_statistics} from "./statistics";
import {addHpoFunctions} from "./utilities";

const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));
const elements = addHpoFunctions();
const phenotypesField = elements.phenotypesField;

$(document).on('click', '#submit-query-button', function(){
    $.ajax({
            type: 'GET',
            headers: {'X-CSRFToken': csrftoken},
            data: {'coordinates': coordinatesField.value, 'phenotypes': phenotypesField.value},
            url: '/single/predict/',
            success: function (response) {
                display_prediction(response);
            },
    });

    draw_statistics(coordinatesField.value, phenotypesField.value);
})

function display_prediction(response) {
    response.models.forEach(function(model) {
        $(`#${model.name}`).html(model.pathogenicity).removeClass('Benign Pathogenic').addClass(`${model.pathogenicity}`);
    })
}