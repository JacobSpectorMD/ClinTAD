import {MDCSelect} from "@material/select";
import {MDCTextField} from "@material/textfield";

const phenotypesField = new MDCTextField(document.querySelector('#phenotypes-field'));
const select = new MDCSelect(document.querySelector('#hpo-select'));

// The functionality for the HPO phenotype lookup forms
export function addHpoFunctions () {

    // Lookup HPOs when the button is pressed
    const hpo_lookup_button = document.querySelector('#hpo-lookup-button');
    hpo_lookup_button.addEventListener('click', function () {
        lookup_hpo(select);
    });

    // Add HPOs to the phenotypes field when the "Add" button is pressed
    const hpo_add_button = document.querySelector('#hpo-add-button');
    hpo_add_button.addEventListener('click', function () {
        add_hpo(select, phenotypesField);
    })

    //Search for phenotype when the user focuses on #hpo-lookup-input and presses enter
    document.getElementById('hpo-lookup-input').onkeypress = function(e) {
        var event = e || window.event;
        var charCode = event.which || event.keyCode;
        if (charCode == '13') {
            lookup_hpo(select);
        };
    }

    return {'select': select, 'phenotypesField': phenotypesField}
}

function lookup_hpo (select) {
    const add_hpo_ul = document.querySelector('#add-hpo-ul');
    add_hpo_ul.innerHTML = '';
    document.getElementById("hpo-lookup-input").innerHTML = "";
    const input_text = document.getElementById('hpo-lookup-input').value;

    $.getJSON("/single/get_phenotypes/", input_text, function(phenotypes){
        for (let i=0; i < phenotypes.length; i++) {
            let item = phenotypes[i];
            let option;
            if (i === 0) {
                option = $(`
                    <li class="mdc-list-item mdc-list-item--selected" role="option" data-value="${item}" tabindex="0" aria-selected>
                        <span class="mdc-list-item__text">${item}</span>
                    </li>
                `);
                $('hpo-selected-text').html(item);
            } else {
                option = $(`
                    <li class="mdc-list-item" role="option" data-value="${item}" tabindex="-1">
                        <span class="mdc-list-item__text">${item}</span>
                    </li>
                `);
            }
            $(add_hpo_ul).append(option);
        }
        select.layoutOptions();
        select.setSelectedIndex(0);
        // $('#add-hpo-select .mdc-floating-label').addClass('mdc-floating-label--float-above');
    });
    // document.getElementById('add-hpo-select').focus();
}

// Adds a selected HPO to the phenotypes input field
function add_hpo (select, phenotypesField){
    console.log(select, select.value);
    let hpo_string = select.value;
    const hpo_id = hpo_string.split("-")[0];
    
    // Don't add duplicate values
    if (phenotypesField.value.includes(hpo_id)) { return }

    if (phenotypesField.value !== "") {
        phenotypesField.value = phenotypesField.value + ", " + hpo_id;
    } else if(phenotypesField.value === "") {
        phenotypesField.value = hpo_id;
    }
}