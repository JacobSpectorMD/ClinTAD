import {MDCTextField} from "@material/textfield";

import { addHpoFunctions } from './utilities';
import { csrftoken } from '../js/utilities.js';

const elements = addHpoFunctions();
const select = elements.select;
const phenotypesField = elements.phenotypesField;
const coordinatesField = new MDCTextField(document.querySelector('#coordinates-field'));
const dataField = new MDCTextField(document.querySelector('#data-field'));
const caseField = new MDCTextField(document.querySelector('#case-field'));

let toggle_choice = 'cases';
const multiple_cases_placeholder = "Separate data by tabs and cases by returns, e.g. &#10;Case 1  chr1:80000-90000  HP:0410034, 717&#10;Case 2  chr2:70000-90000  1863, 717";
const multiple_regions_placeholder = "Enter phenotypes on the first line separated by commas. Enter coordinates on subsequent lines. For example:&#10;7, 10, 512&#10;Chr1:5,000,000-8,500,000"

$(document).on('click', '#case-toggle-div', function(){
    move_toggle();
});

function move_toggle(){
    var rect = d3.select('#toggle_rect');
    var bbox = rect.node().getBBox();
    var rect_length = bbox.width;

    var triangle = d3.select('#toggle_triangle');
    bbox = triangle.node().getBBox();
    var triangle_width = bbox.width;
    var triangle_height = bbox.height;

    var start_x = bbox.x + bbox.width/2;
    var start_y = bbox.y+bbox.height/2;

    var x_translate = rect_length + triangle_width;

    var cases_text = d3.select('#multiple_cases_text');
    var regions_text = d3.select('#multiple_regions_text');
    
    dataField.value = '';
    
    // Switch between inputs for multiple cases and multiple regions
    if (toggle_choice == 'cases'){
        // Roll the triangle and fade text on the toggle button
        var triangle = d3.select('#toggle_triangle')
            .transition().duration(1000)
            .attrTween('transform', function() {
                return d3.interpolateString('translate(0,0) rotate(0,'+start_x+','+start_y+')',
                    'translate('+x_translate+',0) rotate(180,'+start_x+','+start_y+')');
            });
        cases_text.transition().duration(1000).style("opacity", 0.5);
        regions_text.transition().duration(1000).style("opacity", 1);

        // Hide the case identifier input
        $('#case-div').fadeOut(840);

        toggle_choice = 'regions';
    } else {
        // Roll the triangle and fade text on the toggle button
        var triangle = d3.select('#toggle_triangle')
            .transition().duration(1000)
            .attrTween('transform', function() {
                return d3.interpolateString('translate('+x_translate+',0) rotate(180,'+start_x+','+start_y+')',
                    'translate(0,0) rotate(0,'+start_x+','+start_y+')');
            });
        cases_text.transition().duration(1000).style("opacity", 1);
        regions_text.transition().duration(1000).style("opacity", 0.5);

        $('#case-div').fadeIn(840);

        toggle_choice = 'cases';
    }

}


$(document).on('click', '#submit-data-button', function() { submit_multiple() })

function submit_multiple (){
    var text = dataField.value;

    var multiple_data = {'cases_or_regions': toggle_choice, 'text': text};

    $.ajax({
        type: "POST",
        url: "/multiple_submit/",
        data: multiple_data,
        headers: {'X-CSRFToken': csrftoken},
        success: function(response){
            console.log(response);
            // Remove old results from table
            $('.result_row').remove();
            response.clintad_data.forEach(function(result){
                display_results(result);
            })
        },
    })
}

const inheritance = {
    'autosomal-dominant': '',
    'autosomal-recessive': '',
    'x-linked-dominant': '',
    'x-linked-recessive': '',
}

function display_results(result) {
    var table = document.getElementById('results-table-body');
    var row = table.insertRow(-1);
    row.className = "result-row";

    var idCell = row.insertCell(0);
    idCell.innerHTML = result.case_id;

    var coordinateCell = row.insertCell(1);
    coordinateCell.innerHTML = 'chr' + result.chromosome+ ':' + result.cnv_start + '-' + result.cnv_end;

    var phenotypesCell = row.insertCell(2);
    phenotypesCell.innerHTML = result.phenotypes;

    var geneMatchesCell = row.insertCell(3);
    var geneMatchesList = [];
    result.genes.forEach(function(gene){
        if (gene.matches.length == 0){return}
        const matchList = []
        gene.matches.forEach(function(match){
            matchList.push(match.hpo);
        })
        geneMatchesList.push(gene.name+'('+matchList.join(',')+')');
    })
    geneMatchesCell.innerHTML = geneMatchesList.join(', ');

    // Fill in the inheritance cells
    var autosomalDominantCell = row.insertCell(4);
    autosomalDominantCell.className = `autosomal-dominant ${inheritance['autosomal-dominant']}`;
    autosomalDominantCell.innerHTML = get_inheritance(result, 'autosomal_dominant');

    var autosomalRecessiveCell = row.insertCell(5);
    autosomalRecessiveCell.className = `autosomal-recessive ${inheritance['autosomal-recessive']}`;
    autosomalRecessiveCell.innerHTML = get_inheritance(result, 'autosomal_recessive');

    var xLinkedDominantCell = row.insertCell(6);
    xLinkedDominantCell.className = `x-linked-dominant ${inheritance['x-linked-dominant']}`;
    xLinkedDominantCell.innerHTML = get_inheritance(result, 'x_linked_dominant');

    var xLinkedRecessiveCell = row.insertCell(7);
    xLinkedRecessiveCell.className = `x-linked-recessive ${inheritance['x-linked-recessive']}`;
    xLinkedRecessiveCell.innerHTML = get_inheritance(result, 'x_linked_recessive');
}

function get_inheritance(result, inheritance){
    var omim_dict = {};
    result.genes.forEach(function(gene){
        for (var omim_id in gene[inheritance]){omim_dict[omim_id] = true}
    })

    var omim_list = [];
    for (var omim_id in omim_dict){
        omim_list.push('<a href="https://omim.org/entry/'+omim_id+'" target="_blank"> OMIM:'+omim_id+'</a>');
    }
    return omim_list.join(', ');
}

// Add the inputs in multiple cases inputs to the textarea
$(document).on('click', '#add-case-button', function() {
    const coordinates = coordinatesField.value;
    const phenotypes = phenotypesField.value;
    
    if (toggle_choice === 'cases') {
        add_case(coordinates, phenotypes);
    } else if (toggle_choice === 'regions') {
        add_region(coordinates, phenotypes);
    }

    caseField.value = '';
    coordinatesField.value = '';
})

function add_case(coordinates, phenotypes) {
    if (coordinates == ''){
        alert('Please enter valid coordinates');
        return;
    }
    const caseId = caseField.value;
    dataField.value += `${caseId}\t${coordinates}\t${phenotypes}\n`;
    phenotypesField.value = '';
}

// Adds a region to #data-field based on user input. Updates the phenotypes to whatever is in phenotypesField.
function add_region(coordinates, phenotypes) {
    if (dataField.value === '') {
        dataField.value = `${phenotypes}\n${coordinates}\n`;
    }   else {
        const currentText = dataField.value.split('\n');
        const newRegions = [];
        newRegions.push(phenotypes);
        
        // Keep the old coordinates that were entered
        for (let i = 1; i < currentText.length; i++) {
            let region = currentText[i];
            if (region !== '') {newRegions.push(region);}
        }

        // If coordinates are blank, just update the phenotypes
        if (coordinates !== '') {
            newRegions.push(coordinates);
        }

        dataField.value = newRegions.join('\n');
    }
}

// Show or hide result columns when the column options buttons are clicked
$(document).on('click', '#results-options-div > button', function(){
    var button_class = $(this).attr('class').replace('show', '').replace('hide', '').trim();

    if ($(this).hasClass('show')){
        $('#results_table td.'+button_class).css('display', 'none').addClass('hide');
        $(this).removeClass('show').addClass('hide');
    } else if ($(this).hasClass('hide')){
        $('#results_table td.'+button_class).css('display', 'table-cell').addClass('show');
        $(this).removeClass('hide').addClass('show');
    }
})

$(document).on('click', '#save_as_text_button', function (){
    var return_content = [];
    var return_string = '';
    $('#results_table > tbody tr').each(function (idx, elem){
        var element_text = [];
        $(elem).children('td').each(function (index, child_element){
            element_text.push($(child_element).text());
        });
        return_content.push(`${element_text.join('\t')}`);
    });
    return_string = return_content.join('\r\n');
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(return_string));
    element.setAttribute('download', 'data.txt');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
})


// Highlight the inheritance columns when the header is hovered
$(document).on('mouseover', '.toggle-col', function() {
    const toggleClass = $(this).data('toggle-class');
    $('.'+toggleClass).css('background-color', 'var(--mdc-theme-primary-50)');
})

$(document).on('mouseout', '.toggle-col', function() {
    const toggleClass = $(this).data('toggle-class');
    $('.'+toggleClass).css('background-color', 'unset');
})

// Turn off inheritance columns when the header is clicked
$(document).on('click', '.toggle-col', function() {
    const toggleClass = $(this).data('toggle-class');
    $('.'+toggleClass).toggleClass('hidden');
    if (inheritance[toggleClass] === '') {
        inheritance[toggleClass] = 'hidden';
    } else {
        inheritance[toggleClass] = '';
    }
})