function open_statistics(){
    var url = '/single/statistics/?chr='+$("#id_chromosome").val()+'&start='+$("#id_start").val()+'&end='+$("#id_end").val()+
    '&phenotypes='+$("#id_phenotypes").val();
    window.open(url, "_blank");
}

var dataList = document.getElementById('HPO');
window.onload = function(){
    //Search for phenotype when the user fills the "HPO Phenotype Lookup" form and presses enter
    document.getElementById('HPO_lookup').onkeypress = function(e) {
        var event = e || window.event;
        var charCode = event.which || event.keyCode;
        var input = document.getElementById('HPO_lookup').value;

        if (charCode == '13') {
            lookup_HPO();
        };
    }

    document.getElementById('HPO').onkeypress = function(e) {
        var event = e || window.event;
        var charCode = event.which || event.keyCode;
        var input = document.getElementById('HPO_lookup').value;
        if (charCode == '13') {
            add_HPO();
        };
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
    if(document.getElementById("id_phenotypes").value != ""){
        document.getElementById("id_phenotypes").value = document.getElementById("id_phenotypes").value + ", " + hpo_value_split;
    }
    else if(document.getElementById("id_phenotypes").value == ""){
        document.getElementById("id_phenotypes").value = hpo_value_split;
    }
    document.getElementById("HPO_lookup").value = "";
    document.getElementById("HPO").innerHTML = "";
};

const numberWithCommas = (x) => {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

d3.json("/single/get_genes/", function(response){
    data = JSON.parse(response);
    if (!data){return}
    console.log(data);
    var width=$(window).width()*1.03,
        start_coord = data.minimum['coord'],
        end_coord = data.maximum['coord'];

    var scale_factor = (end_coord - start_coord);
    if ((end_coord - start_coord) > 4000000){
        width = width * scale_factor/4000000;
    }
    data.width = width;

    var scale = d3.scale.linear()
                    .domain([start_coord-(scale_factor*0.05), end_coord+(scale_factor*0.03)])
                    .range([5, width]);

    // Keep track of total height of all tracks
    var total_height = 165;
    // Keep track of the number of tracks drawn, so the background colors can alternate
    var num_tracks = 2;

    // Create the TAD svg
    var tad_svg = draw_tads(data, data.tads, scale);
    draw_boundaries(tad_svg, scale, data.tads, 110, start_coord, end_coord, boundaries_only=false);

    // Create the user CNV and genes svg
    var cnv_gene_svg = draw_cnv_genes(data, scale);
    draw_boundaries(cnv_gene_svg, scale, data.tads, 0, start_coord, end_coord);
    total_height += parseInt(cnv_gene_svg.style('height').replace("px", ""));

    // Enhancer svg
    if (data.default_enhancers){
        var enhancer_svg = draw_enhancers(data, scale, num_tracks);
        draw_boundaries(enhancer_svg, scale, data.tads, 0, start_coord, end_coord);
        num_tracks++;
        total_height += parseInt(enhancer_svg.style('height').replace("px", ""));
    }

    // Benign CNV svg (from Database of Genomic Variants)
    if (data.default_cnvs){
        var cnv_svg = draw_cnvs(data, scale, num_tracks);
        draw_boundaries(cnv_svg, scale, data.tads, 0, start_coord, end_coord);
        num_tracks++;
        total_height += parseInt(cnv_svg.style('height').replace("px", ""));
    }

    // Draw all of the users custom tracks
    data.tracks.forEach(function(track){
        var track_svg = draw_track(data, track, scale, num_tracks);
        draw_boundaries(track_svg, scale, data.tads, 0, start_coord, end_coord);
        num_tracks++;
        total_height += parseInt(track_svg.style('height').replace("px", ""));
    })

    $('#container').css('height', total_height);
})

function draw_tads(data, tads, scale){
    var height = 140;
    var width=data.width;

    var svg = d3.select('#container').append('svg').attr('width', width).attr('height', height);
    var g_0 = svg.append('g').attr('class', 'g_0'),
        g_1 = svg.append('g').attr('class', 'g_1'),
        g_2 = svg.append('g').attr('class', 'g_2');
    var background = g_0.append('rect').attr('width', width).attr('height', height).attr('x', 0).attr('y', 0)
                                       .attr('fill', 'aliceblue');

    var label = g_0.append('text').text('TADs').attr('y', 3+(height/2)).attr('x', 10).attr('font-size', '2em')
                                  .attr('fill', 'rgb(212, 235, 254)').attr('pointer-events', 'none').attr('alignment-baseline', 'middle')
                                  .attr('class', 'track-label');

//    var zoom_in_text = g_2.append('text').text('+').attr('x', 10).attr('y', 24).attr('fill', 'white').attr('pointer-events', 'none')
//                          .attr('font-size', '20');
//    var bbox = zoom_in_text.node().getBBox();
//    var zoom_in_button = g_1.append('rect').attr('x', bbox.x-4).attr('y', bbox.y).attr('width', bbox.width+8).attr('cursor', 'pointer')
//                            .attr('height', bbox.height+1).attr('fill', 'rgb(178, 220, 255)').attr('rx', '4').attr('ry', '4');
//
//    var zoom_out_text = g_2.append('text').text('-').attr('x', 40).attr('y', 24).attr('fill', 'white').attr('pointer-events', 'none')
//                          .attr('font-size', '20');
//    var bbox = zoom_out_text.node().getBBox();
//    var zoom_out_button = g_1.append('rect').attr('x', bbox.x-7).attr('y', bbox.y).attr('width', bbox.width+14).attr('cursor', 'pointer')
//                            .attr('height', bbox.height+1).attr('fill', 'rgb(178, 220, 255)').attr('rx', '4').attr('ry', '4');
//
    var labels_text = g_2.append('text').text('Labels').attr('x', 10).attr('y', 24).attr('fill', 'white').attr('pointer-events', 'none')
                          .attr('font-size', '20');
    var bbox = labels_text.node().getBBox();
    var labels_button = g_1.append('rect').attr('x', bbox.x-3).attr('y', bbox.y).attr('width', bbox.width+6).attr('cursor', 'pointer')
                            .attr('height', bbox.height+1).attr('fill', 'rgb(178, 220, 255)').attr('rx', '4').attr('ry', '4')
                            .on('click', function(){
                                $('.track-label').toggleClass('hidden');
                            });

    return svg;
}

function draw_cnv_genes(data, scale, num_tracks){
    var height = 40;
    var width=data.width;
    var svg = d3.select('#container').append('svg').attr('width', width).attr('height', height);
    var g_0 = svg.append('g').attr('class', 'g_0'),
        g_1 = svg.append('g').attr('class', 'g_1'),
        g_2 = svg.append('g').attr('class', 'g_2');
    var background = g_0.append('rect').attr('width', width).attr('height', height).attr('x', 0).attr('y', 0)
                        .attr('fill', 'var(--light-blue)');

    // Draw the CNV
    svg.append("line")
        .attr("x1", scale(data.cnv_start))
        .attr("y1", 5)
        .attr("x2", scale(data.cnv_end))
        .attr("y2", 5)
        .attr("stroke", "green")
        .attr("stroke-width", 6)
        .on("mouseover", function(){
            var start_label = svg.append("text").attr("x", scale(data.cnv_start)).attr("y", 157).attr("font-size", 10).attr("text-anchor", "middle")
                .attr("font-weight", 550).attr("fill", "green").attr("class", "cnv-label").text(numberWithCommas(data.cnv_start));
            var end_label = svg.append("text").attr("x", scale(data.cnv_end)).attr("y", 157).attr("font-size", 10).attr("text-anchor", "middle")
                .attr("font-weight", 550).attr("fill", "green").attr("class", "cnv-label").text(numberWithCommas(data.cnv_end));
        }).on("mouseout", function(){
            d3.selectAll(".cnv-label").remove();
        })

    var last_end_point = [0];
    var data_to_display = [];
    var genes = data.genes;
    var max_row = 0;
    for(var i = 0; i < genes.length; i++){
        var stroke_color = "blue";
        if (genes[i].phenotype_score > 0){stroke_color = "orange"};

        // End of gene rectangle
        var end_point = scale(genes[i].start)+10;
        if (scale(genes[i].end)>end_point){end_point = scale(genes[i].end);}

        var row = 0;
        var overlap = true;
        while(overlap){
            if (i == 0){
                last_end_point[0] = end_point;
                overlap = false;
            }
            else if (row >= last_end_point.length){
                last_end_point.push(end_point);
                overlap = false;
            }
            else if (scale(genes[i].start) >= last_end_point[row] + 3){
                last_end_point[row] = end_point;
                overlap = false;
            }
            else if (scale(genes[i].start) < last_end_point[row] + 3){
                    row += 1;
                    console.log(scale(genes[i].start));
            }
        };

        if (row > max_row){max_row = row};

        data_to_display.push({
            "Name": genes[i].name,
            "Start": genes[i].start,
            "End": genes[i].end,
            "Number of matches": genes[i].phenotype_score,
            "Matches": genes[i].matches,
            "Phenotypes": genes[i].phenotypes,
        });

        // Draw the gene
        svg.append("line")
            .attr("x1", scale(genes[i].start))
            .attr("y1", 31+row*11)
            .attr("x2", end_point)
            .attr("y2", 31+row*11)
            .attr("stroke", stroke_color)
            .attr("stroke-width", 10)
            .attr("cursor", "pointer")
            .attr("data-name", genes[i].name)
            .attr("data-x1", scale(genes[i].start))
            .attr("data-stroke_color", stroke_color)
            .attr("data-gene_number", i)
            .on("mouseover", function(){
                d3.select(this).attr("stroke", "black");
                var x1 = parseInt(d3.select(this).attr('data-x1'));
                svg.append("text")
                    .text(this.getAttribute("data-name"))
                    .attr("x", function(){
                        if (x1 >= 0){return x1}
                        else {return 0}
                    })
                    .attr("y", 22)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select(this).attr("stroke", this.getAttribute("data-stroke_color"))
                d3.select("#hoverText").remove()
            })
            .on("click", function(){
                //Clears all data from the Selected Data panel
                var element = document.getElementById("patient-data-display");
                while (element.firstChild) {
                    element.removeChild(element.firstChild);
                }

                $("#collapse2").collapse("show");
                $("#collapse1").collapse("hide");

                //Adds information about the clicked object to the Patient Data Display panel
                //Need to work on how these are added!
                var gene_number = this.getAttribute("data-gene_number");
                var selectedDataDisplay = document.getElementById("patient-data-display");
                var selectedBody = document.createElement("tbody");
                var selectedTable = document.createElement("table");
                selectedTable.setAttribute("class", "selected-data");
                var values = data_to_display[gene_number];
                Object.keys(values).forEach(function(key) {
                    if(key!="Phenotypes" && key!="Matches"){
                        var row = document.createElement("tr");
                        var cell = document.createElement("td");
                        cell.setAttribute("width", "20%");
                        var cellText = document.createTextNode(key+": ");
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        var cell = document.createElement("td");
                        var cellText = document.createTextNode(values[key]);
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        selectedBody.appendChild(row);
                    }
                });

                // Add the HPOs for the clicked gene
                var row = document.createElement("tr");
                var cell = document.createElement("td");
                cell.setAttribute("width", "20%");
                var cellText = document.createTextNode("Matches: ");
                cell.appendChild(cellText);
                row.appendChild(cell);
                var cell = document.createElement("td");
                var match_ids = [];
                values['Matches'].forEach(function(hpo){
                    match_ids.push(hpo.hpo);
                    var hpo_span = document.createElement("SPAN");
                    hpo_span.innerHTML = hpo.name+', ';
                    hpo_span.setAttribute("data-hpoid", hpo.hpo);
                    hpo_span.setAttribute("class", "match");
                    hpo_span.setAttribute("title", hpo.hpo);
                    cell.appendChild(hpo_span);
                })
                row.appendChild(cell);
                selectedBody.appendChild(row);

                // Add the HPOs for the clicked gene
                var row = document.createElement("tr");
                var cell = document.createElement("td");
                cell.setAttribute("width", "20%");
                var cellText = document.createTextNode("Phenotypes: ");
                cell.appendChild(cellText);
                row.appendChild(cell);
                var cell = document.createElement("td");
                values['Phenotypes'].forEach(function(hpo){
                    var hpo_span = document.createElement("SPAN");
                    hpo_span.innerHTML = hpo.name+', ';
                    hpo_span.setAttribute("data-hpoid", hpo.hpo);
                    if ($.inArray(hpo.hpo, match_ids)!=-1){ // Give phenotypes with matches the match class
                        hpo_span.setAttribute("class", "match");
                    } else {
                        hpo_span.setAttribute("class", "hpo");
                    }
                    hpo_span.setAttribute("title", hpo.hpo);
                    cell.appendChild(hpo_span);
                })
                row.appendChild(cell);
                selectedBody.appendChild(row);

                selectedTable.appendChild(selectedBody);
                selectedDataDisplay.appendChild(selectedTable);
        });
    };

    if (max_row > 0){
        height += max_row*11;
        svg.attr('height', height);
        background.attr('height', height);
    }
    var label = g_0.append('text').text('CNV / Genes').attr('y', 3+(height/2)).attr('x', 10).attr('font-size', '2em')
                              .attr('fill', 'white').attr('pointer-events', 'none').attr('alignment-baseline', 'middle')
                              .attr('class', 'track-label');
    return svg;
}

function draw_enhancers(data, scale){
    var height = 30;
    var width=data.width;
    var svg = d3.select('#container').append('svg').attr('width', width).attr('height', height);
    var g_0 = svg.append('g').attr('class', 'g_0'),
        g_1 = svg.append('g').attr('class', 'g_1'),
        g_2 = svg.append('g').attr('class', 'g_2');
    var background = g_0.append('rect').attr('width', width).attr('height', height).attr('x', 0).attr('y', 0)
                        .attr('fill', 'aliceblue');
    var label = g_0.append('text').text('VISTA').attr('y', 3+(height/2)).attr('x', 10).attr('font-size', '2em')
                          .attr('fill', 'rgb(212, 235, 254)').attr('pointer-events', 'none').attr('alignment-baseline', 'middle')
                          .attr('class', 'track-label');

    data.enhancers.forEach(function(enhancer){
        var line = svg.append("line")
            .attr("x1", scale(enhancer.start))
            .attr("x2", function(){
                if (scale(enhancer.end)-scale(enhancer.start)>10){
                    return scale(enhancer.end);
                } else {
                    return scale(enhancer.end)+10;
                }
            })
            .attr("data-vista", enhancer.vista_element).attr("y1", 23).attr("y2", 23).attr("stroke", "purple").attr("stroke-width", 6)
            .attr("class", "enhancer")
            .on("mouseover", function(){
                svg.append("text")
                    .text("Vista "+$(this).data("vista")).attr("text-anchor", "middle")
                    .attr("x", scale(enhancer.start))
                    .attr("y", 15)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select("#hoverText").remove()
            })
    })

    return svg;
}

function draw_cnvs(data, scale, num_tracks){
    var height = 40;
    var width = data.width;
    var svg = d3.select('#container').append('svg').attr('width', width).attr('height', height);
    var g_0 = svg.append('g').attr('class', 'g_0'),
        g_1 = svg.append('g').attr('class', 'g_1'),
        g_2 = svg.append('g').attr('class', 'g_2');
    var color = track_color(num_tracks);
    var background = g_0.append('rect').attr('width', width).attr('height', height).attr('x', 0).attr('y', 0)
                        .attr('fill', color['fill']);

    var last_end_point = [0];
    var data_to_display = [];
    var variants = data.variants;
    var max_row = 0;
    for(var i = 0; i < variants.length; i++){
        if (variants[i].subtype == 'gain'){var stroke_color = 'blue'}
        else {var stroke_color = 'red'}
        var opacity = (variants[i].frequency >= 1) ? 1 : 0.5;

        // End of gene rectangle
        var end_point = scale(variants[i].outer_start)+10;
        if (scale(variants[i].outer_end)>end_point){end_point = scale(variants[i].outer_end);}

        var row = 0;
        var overlap = true;
        while(overlap){
            if (i == 0){
                last_end_point.push(end_point);
                overlap = false;
            }
            else if (row >= last_end_point.length){
                last_end_point.push(end_point);
                overlap = false;
            }
            else if (scale(variants[i].outer_start) >= last_end_point[row] + 3){
                last_end_point[row] = end_point;
                overlap = false;
            }
            else if (scale(variants[i].outer_start) < last_end_point[row] + 3){
                    row += 1;
            }
        };

        if (row > max_row){max_row = row};

        data_to_display.push({
            "Variant ID/Accession": variants[i].accession,
            "Gain or Loss": variants[i].subtype,
            "Chromosome": variants[i].chromosome,
            "Outer Start": variants[i].outer_start,
            "Inner Start": variants[i].inner_start,
            "Inner End": variants[i].inner_end,
            "Outer End": variants[i].outer_end,
            "Studies": variants[i].study,
            "Sample Size": variants[i].sample_size,
            "Frequency": variants[i].frequency+'%',
        });

        // Draw the gene
        svg.append("line")
            .attr("x1", scale(variants[i].outer_start))
            .attr("y1", 30+row*11)
            .attr("x2", end_point)
            .attr("y2", 30+row*11)
            .attr("stroke", stroke_color)
            .attr("stroke-width", 10)
            .attr("data-x1", scale(variants[i].outer_start))
            .attr("data-stroke_color", stroke_color)
            .attr("data-gene_number", i)
            .attr("data-accession", variants[i].accession)
            .attr("opacity", opacity)
            .attr("cursor", "pointer")
            .on("mouseover", function(){
                svg.append("text")
                    .text($(this).data("accession")).attr("text-anchor", "middle")
                    .attr("x", $(this).data("x1"))
                    .attr("y", 15)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select("#hoverText").remove()
            })
            .on("click", function(){
                //Clears all data from the Selected Data panel
                var element = document.getElementById("patient-data-display");
                while (element.firstChild) {
                    element.removeChild(element.firstChild);
                }

                $("#collapse2").collapse("show");
                $("#collapse1").collapse("hide");

                //Adds information about the clicked object to the Patient Data Display panel
                //Need to work on how these are added!
                var gene_number = this.getAttribute("data-gene_number");
                var selectedDataDisplay = document.getElementById("patient-data-display");
                var selectedBody = document.createElement("tbody");
                var selectedTable = document.createElement("table");
                selectedTable.setAttribute("class", "selected-data");
                var values = data_to_display[gene_number];
                Object.keys(values).forEach(function(key) {
                    if(key!="Phenotypes" && key!="Matches"){
                        var row = document.createElement("tr");
                        var cell = document.createElement("td");
                        cell.setAttribute("width", "20%");
                        var cellText = document.createTextNode(key+": ");
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        var cell = document.createElement("td");
                        var cellText = document.createTextNode(values[key]);
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        selectedBody.appendChild(row);
                    }
                });

                selectedTable.appendChild(selectedBody);
                selectedDataDisplay.appendChild(selectedTable);
        });
    };

    if (max_row > 0){
        height += max_row*12;
        svg.attr('height', height);
        background.attr('height', height);
    }
    var label = g_0.append('text').text('DGV').attr('y', 3+(height/2)).attr('x', 10).attr('font-size', '2em')
                              .attr('fill', color['text']).attr('pointer-events', 'none')
                              .attr('class', 'track-label').attr('alignment-baseline', 'middle');
    return svg;
}


function draw_track(data, track, scale, num_tracks){
    var height = 40;
    var width=data.width;
    var svg = d3.select('#container').append('svg').attr('width', width).attr('height', height);
    var g_0 = svg.append('g').attr('class', 'g_0'),
        g_1 = svg.append('g').attr('class', 'g_1'),
        g_2 = svg.append('g').attr('class', 'g_2');
    var color = track_color(num_tracks);
    var background = g_0.append('rect').attr('width', width).attr('height', height).attr('x', 0).attr('y', 0)
                        .attr('fill', color['fill']);

    var last_end_point = [0];
    var data_to_display = [];
    var elements = track.elements;
    var max_row = 0;
    for(var i = 0; i < elements.length; i++){
        if (track.color){var stroke_color=track.color}
        else {var stroke_color = "blue";}

        // End of gene rectangle
        var end_point = scale(elements[i].start)+10;
        if (scale(elements[i].end)>end_point){end_point = scale(elements[i].end);}

        var row = 0;
        var overlap = true;
        while(overlap){
            if (i == 0){
                last_end_point.push(end_point);
                overlap = false;
            }
            else if (row >= last_end_point.length){
                last_end_point.push(end_point);
                overlap = false;
            }
            else if (scale(elements[i].start) >= last_end_point[row] + 3){
                last_end_point[row] = end_point;
                overlap = false;
            }
            else if (scale(elements[i].start) < last_end_point[row] + 3){
                    row += 1;
            }
        };

        if (row > max_row){max_row = row};

        data_to_display.push({
            "Chromosome": elements[i].chromosome,
            "Start": elements[i].start,
            "End": elements[i].end,
            "Details": elements[i].details,
        });

        // Draw the element
        svg.append("line")
            .attr("x1", scale(elements[i].start))
            .attr("y1", 30+row*11)
            .attr("x2", end_point)
            .attr("y2", 30+row*11)
            .attr("stroke", stroke_color)
            .attr("stroke-width", 10)
            .attr("data-x1", scale(elements[i].start))
            .attr("data-stroke_color", stroke_color)
            .attr("data-gene_number", i)
            .attr("data-label", elements[i].label)
            .attr("cursor", "pointer")
            .on("mouseover", function(){
                svg.append("text")
                    .text($(this).data("label")).attr("text-anchor", "middle")
                    .attr("x", $(this).data("x1"))
                    .attr("y", 15)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select("#hoverText").remove()
            })
            .on("click", function(){
                //Clears all data from the Selected Data panel
                var element = document.getElementById("patient-data-display");
                while (element.firstChild) {
                    element.removeChild(element.firstChild);
                }

                $("#collapse2").collapse("show");
                $("#collapse1").collapse("hide");

                //Adds information about the clicked object to the Patient Data Display panel
                //Need to work on how these are added!
                var gene_number = this.getAttribute("data-gene_number");
                var selectedDataDisplay = document.getElementById("patient-data-display");
                var selectedBody = document.createElement("tbody");
                var selectedTable = document.createElement("table");
                selectedTable.setAttribute("class", "selected-data");
                var values = data_to_display[gene_number];
                Object.keys(values).forEach(function(key) {
                    if(key!="Phenotypes" && key!="Matches"){
                        var row = document.createElement("tr");
                        var cell = document.createElement("td");
                        cell.setAttribute("width", "20%");
                        var cellText = document.createTextNode(key+": ");
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        var cell = document.createElement("td");
                        var cellText = document.createTextNode(values[key]);
                        cell.appendChild(cellText);
                        row.appendChild(cell);
                        selectedBody.appendChild(row);
                    }
                });

                selectedTable.appendChild(selectedBody);
                selectedDataDisplay.appendChild(selectedTable);
        });
    };

    if (max_row > 0){
        height += max_row*10;
        svg.attr('height', height);
        background.attr('height', height);
    }
    var label = g_0.append('text').text(track.label).attr('y', 3+(height/2)).attr('x', 10).attr('font-size', '2em')
                              .attr('fill', color['text']).attr('pointer-events', 'none')
                              .attr('class', 'track-label').attr('alignment-baseline', 'middle');
    return svg;
}

function draw_boundaries(svg, scale, tads, y1, start_coord, end_coord, boundaries_only=true){
    var layer = svg.select('.g_0');


    function draw_dashed(coord, side, drawText){
        layer.append("line")
            .attr("x1", scale(coord))
            .attr("y1", y1)
            .attr("x2", scale(coord))
            .attr("y2", svg.style('height'))
            .style("stroke", "#ff8080")
            .style("stroke-width", 3)
            .style("stroke-dasharray", ("3, 3"));

        if (!boundaries_only){
             //Adds the coordinate text
            if (side=="l"){
                layer.append("text").attr("x", scale(coord)+2).attr("text-anchor", "start").text(coord.toLocaleString())
                    .attr("y", 125).style("font-size", 12).style("font-weight", 600).style("font-family", "arial");
            }
            else if (side=="r" && drawText){
                layer.append("text").attr("x", scale(coord)-2).attr("text-anchor", "end").text(coord.toLocaleString())
                    .attr("y", 135).style("font-size", 12).style("font-weight", 600).style("font-family", "arial");
            };
        }

    }

    // Loop through list of tads and draw the TADs and boundaries
    for(var i = 0; i < tads.length; i++){
        var left = tads[i]['start'];
        var right = tads[i]['end'];
        var mid = (left+right)/2;

        if (boundaries_only==false){
            console.log(mid);
            //Draws a triangle path to represent the TAD
            layer.append("path")
            .attr("d", "M "+scale(left)+" 110 "+
                       "L "+scale(mid)+" 10 "+
                       "L "+scale(right)+" 110")
            .style("stroke", "red")
            .style("stroke-width", 3)
            .style("fill", "none");
        }

        //Draws dashed lines at the boundary coordinates
        draw_dashed(left, "l", true);
        if(i<tads.length-1){
            if(right==tads[i+1]['start']){draw_dashed(right, "r", false)};
            if(right!=tads[i+1]['start']){draw_dashed(right, "r", true)};
        } else {
            draw_dashed(right, "r", true);
        }
    }

    // Draw dashed line for chromosome end if necessary
    if (data.minimum['type']=='chromosome'){draw_dashed(start_coord, "l", true);}
    if (data.maximum['type']=='chromosome'){draw_dashed(end_coord, "r", true);}
} // End of draw_boundaries

function track_color(num_tracks){
    if (num_tracks%2==0){
        return {'fill': 'aliceblue', 'text': 'var(--light-blue)'}
    } else {
        return {'fill': 'var(--light-blue)', 'text': 'white'}
    }
}
