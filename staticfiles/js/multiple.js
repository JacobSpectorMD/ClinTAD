import { csrftoken } from './utilities.js';

var toggle_choice = 'cases';
var multiple_cases_placeholder = "Separate data by tabs and cases by returns, e.g. &#10;Case 1  chr1:80000-90000  HP:0410034, 717&#10;Case 2  chr2:70000-90000  1863, 717";
var multiple_regions_placeholder = "Enter phenotypes on the first line separated by commas. Enter coordinates on subsequent lines. For example:&#10;7, 10, 512&#10;Chr1:5,000,000-8,500,000"

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
        
        // Switch information displayed near toggle button
        $('#multiple_cases_info').delay(875).fadeIn(1000);
        $('#multiple_regions_info').fadeOut(840);
        
        // Add 'active' class to phenotype_input being shown
        $('#multiple_regions_div .phenotype_input').removeClass('active');
        $('#multiple_cases_div .phenotype_input').addClass('active');
        
        // Fade out current inputs, and fade in new ones
        console.log($('#multiple_cases_div').height(), $('#multiple_cases_div').innerHeight() );
        $('#cases_and_regions_div').animate({height: $('#multiple_cases_div').innerHeight()}, 550);
        $('#multiple_regions_div').fadeOut(500);
        $('#multiple_cases_div').delay(600).fadeIn(500);
        $('#multiple-textarea').attr("placeholder", multiple_cases_placeholder);

        toggle_choice = 'cases';
    }

}

function lookup_HPO(){
    document.getElementById("HPO").innerHTML = "";
    var input_text = document.getElementById('HPO_lookup').value;
    var inputs = input_text.split(" ");
    data = {inputs: inputs};
    $.getJSON("/single/get_phenotypes/", input_text, function(phenotypes){
        var phenotypelist = phenotypes;
        phenotypelist.forEach(function(item){
            var option = document.createElement('option');
            option.value = item;
            option.text = item;
            HPO.appendChild(option);
        });
    });
    document.getElementById('HPO').focus();
};

function add_HPO(){
    var hpo_value = document.getElementById("HPO").value;
    hpo_value = hpo_value.split("-");
    var hpo_value_split = hpo_value[0];
    
    var current_phenotype_val = $('.phenotype_input.active').val();
    if(current_phenotype_val != ""){
        $('.phenotype_input').val(current_phenotype_val + ", " + hpo_value_split);
    }
    else if(current_phenotype_val == ""){
        $('.phenotype_input').val(hpo_value_split);
    }
    document.getElementById("HPO_lookup").value = "";
    document.getElementById("HPO").innerHTML = "";
};

function submit_multiple(){
    var text = $('#multiple-textarea').val();
    
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

function display_results(result){
    var table = document.getElementById('results_table');
    var row = table.insertRow(-1);
    row.className = "result_row";
    
    var id_cell = row.insertCell(0);
    id_cell.innerHTML = result.case_id;
    
    var coordinate_cell = row.insertCell(1);
    coordinate_cell.innerHTML = 'Chr'+result.chromosome+':'+result.cnv_start+'-'+result.cnv_end;
    
    var phenotypes_cell = row.insertCell(2);
    phenotypes_cell.innerHTML = result.phenotypes;
    
    var gene_matches_cell = row.insertCell(3);
    var gene_matches_list = [];
    result.genes.forEach(function(gene){
        if (gene.matches.length == 0){return}
        var match_list = []
        gene.matches.forEach(function(match){
            match_list.push(match.hpo);
        })
        gene_matches_list.push(gene.name+'('+match_list.join(',')+')');
    })
    gene_matches_cell.innerHTML = gene_matches_list.join(', ');
    
    // Fill in the inheritance cells
    var autosomal_dominant_cell = row.insertCell(4);
    autosomal_dominant_cell.className = "autosomal_dominant";
    autosomal_dominant_cell.innerHTML = get_inheritance(result, 'autosomal_dominant');
    
    var autosomal_recessive_cell = row.insertCell(5);
    autosomal_recessive_cell.className = "autosomal_recessive";
    autosomal_recessive_cell.innerHTML = get_inheritance(result, 'autosomal_recessive');
    
    var x_linked_dominant_cell = row.insertCell(6);
    x_linked_dominant_cell.className = "x_linked_dominant";
    x_linked_dominant_cell.innerHTML = get_inheritance(result, 'x_linked_dominant');    
    
    var x_linked_recessive_cell = row.insertCell(7);
    x_linked_recessive_cell.className = "x_linked_recessive";
    x_linked_recessive_cell.innerHTML = get_inheritance(result, 'x_linked_recessive');    
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
$(document).on('click', '#add-input-button', function(){
    var case_id = $('#case-id-input').val();
    var coordinates = $('#coordinates-input').val();
    var phenotypes = $('#phenotypes-input').val();
    var new_text = case_id+'\t'+coordinates+'\t'+phenotypes;
    
    if (coordinates == ''){
        alert('Please enter valid coordinates');
        return;
    }
    
    var current_text = $('#multiple-textarea').val();
    if (current_text != ''){
        $('#multiple-textarea').val(current_text+'\n'+new_text);
    } else {
        $('#multiple-textarea').val(new_text);
    }
    
    $('#case-id-input').val('');
    $('#coordinates-input').val('');
    $('#phenotypes-input').val('');
})

// Add the coordinates for input box in the multiple regions section
$(document).on('click', '#regions-add-button', function(){
    var coordinates = $('#regions-coordinates-input').val();
    if (coordinates == ''){
        alert('Please enter valid coordinates');
        return;
    }
    
    var current_text = $('#multiple-textarea').val();
    if (current_text != ''){
        $('#multiple-textarea').val(current_text+'\n'+coordinates);
    } else {
        $('#multiple-textarea').val(coordinates);
    }
    
    $('#regions-coordinates-input').val('');
})

// When "Set Phenotypes" button is clicked, add the content to the textarea
$(document).on('click', '#set-phenotypes-button', function(){
    var phenotypes = $('#regions-phenotypes-input > input').val();
    
    var current_text = $('#multiple-textarea').val();
    if (current_text != ''){
        var old_lines = current_text.split("\n");
        var new_lines = [];

        // If the first line is not phenotypes already, put phenotypes there and move everything else down
        if (old_lines[0].includes(':')){
            new_lines.push(phenotypes);
            old_lines.forEach(function(line){new_lines.push(line)});
        } 
        // Otherwise, just replace first line
        else {
            old_lines[0] = phenotypes;
            old_lines.forEach(function(line){new_lines.push(line)});
        }
        
        var new_text = new_lines.join("\n");
        $('#multiple-textarea').val(new_text);
    } else {
        $('#multiple-textarea').val(phenotypes);
    }
})

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