import {MDCSelect} from '@material/select';
import {MDCTextField} from '@material/textfield';

const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));
const phenotypesField = new MDCTextField(document.querySelector('#phenotypes-field'));

const select = new MDCSelect(document.querySelector('#hpo-select'));

$(document).ready(function () {
    if (coordinates) {
        coordinatesField.value = coordinates;
    }
    
    if (phenotypes !== '') {
        phenotypesField.value = phenotypes;
    }
})

// Lookup HPOs when the button is pressed
const hpo_lookup_button = document.querySelector('#hpo-lookup-button');
hpo_lookup_button.addEventListener('click', function () {
    lookup_hpo();
});

// Add HPOs to the phenotypes field when the "Add" button is pressed
const hpo_add_button = document.querySelector('#hpo-add-button');
hpo_add_button.addEventListener('click', function () {
    add_hpo();
})

function add_hpo (){
    var hpo_value = select.value;
    hpo_value = hpo_value.split("-");
    var hpo_value_split = hpo_value[0];
    if (phenotypesField.value != "") {
        phenotypesField.value = phenotypesField.value + ", " + hpo_value_split;
    } else if(phenotypesField.value == ""){
        phenotypesField.value = hpo_value_split;
    }
}

//Search for phenotype when the user focuses on #hpo-lookup-input and presses enter
document.getElementById('hpo-lookup-input').onkeypress = function(e) {
    var event = e || window.event;
    var charCode = event.which || event.keyCode;
    if (charCode == '13') {
        lookup_hpo();
    };
}

$(document).on('click', '#track-labels-button', function() {
    $('.track-label').toggleClass('hidden');
})

$(document).on('click', '#statistics-button', function() {
    if (!coordinates || !phenotypes) { return }
    var url = `/single/statistics/?coordinates=${coordinates}&phenotypes=${phenotypes}`;
    window.open(url, "_blank");
})

function lookup_hpo () {
    const add_hpo_ul = document.querySelector('#add-hpo-ul');
    add_hpo_ul.innerHTML = '';
    document.getElementById("hpo-lookup-input").innerHTML = "";
    const input_text = document.getElementById('hpo-lookup-input').value;
    const inputs = input_text.split(" ");
    const data = {inputs: inputs};
    $.getJSON("/single/get_phenotypes/", input_text, function(phenotypes){
        for (let i=0; i < phenotypes.length; i++) {
            let item = phenotypes[i];
            let option;
            if (i === 0) {
                option = $(`
                    <li class="mdc-list-item" role="option" data-value="${item}" tabindex="0" aria-selected>
                        <span class="mdc-list-item__text">${item}</span>
                    </li>
                `);
            } else {
                option = $(`
                    <li class="mdc-list-item" role="option" data-value="${item}" tabindex="-1">
                        <span class="mdc-list-item__text">${item}</span>
                    </li>
                `);   
            }
            $(add_hpo_ul).append(option);
        }
        select.selectedIndex = 0;
        $('#add-hpo-select .mdc-floating-label').addClass('mdc-floating-label--float-above');
    });
    document.getElementById('add-hpo-select').focus();
}