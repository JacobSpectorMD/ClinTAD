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

d3.json("/single/get_genes/", function(d){
    //Draws a dashed line based on the coordinate it was passed
    function drawDashed(coord, side, drawText){
        canvas.append("line")
            .attr("x1", scale(coord))
            .attr("y1", 110)
            .attr("x2", scale(coord))
            .attr("y2", canvasHeight)
            .style("stroke", "#ff8080")
            .style("stroke-width", 3)
            .style("stroke-dasharray", ("3, 3"));

        //Adds the coordinate text
        if (side=="l"){
            canvas.append("text")
                .attr("x", scale(coord)+2)
                .attr("y", 125)
                .attr("text-anchor", "start")
                .text(coord.toLocaleString())
                    .style("font-size", 12)
                    .style("font-weight", 600)
                    .style("font-family", "arial");
        }

        else if (side=="r" && drawText){
            canvas.append("text")
                .attr("x", scale(coord)-2)
                .attr("y", 135)
                .attr("text-anchor", "end")
                .text(coord.toLocaleString())
                    .style("font-size", 12)
                    .style("font-weight", 600)
                    .style("font-family", "arial");
        };
    } // End of drawDashed

    data = JSON.parse(d);
    console.log(data);
    var container = d3.select("#container");

    var canvas_width=$(window).width()*1.03;
    var canvasHeight = 400;
    var start_coord = data.minimum['coord'];
    var end_coord = data.maximum['coord'];
    var end_type = data.maximum['type'];
    var scale_factor = (end_coord - start_coord);
    if ((end_coord - start_coord) > 4000000){
        canvas_width = canvas_width * scale_factor/4000000;
    }

    var scale = d3.scale.linear()
                    .domain([start_coord-(scale_factor*0.05), end_coord+(scale_factor*0.03)])
                    .range([5, canvas_width]);

    var canvas = container.append("svg")
        .attr("width", canvas_width)
        .attr("id", "canvas")
        .attr("height", canvasHeight)
        .attr("class", "graph-svg-component");

    // ??
    $('#container').scrollLeft(scale(0.99*data.cnv_start));

    // Draw the TADs and boundaries
    var tads = data.tads;
    for(var i = 0; i < tads.length; i++){
        var left = tads[i]['left'];
        var right = tads[i]['right'];
        var mid = (left+right)/2;

        //Draws a triangle path to represent the TAD
        canvas.append("path")
            .attr("d", "M "+scale(left)+" 110"+"L "+scale(mid)+" 10"
                  +"L "+scale(right)+" 110")
            .style("stroke", "red")
            .style("stroke-width", 3)
            .style("fill", "none")

        //Draws dashed lines at the boundary coordinates
        drawDashed(left, "l", true);
        if(i<tads.length-1){
            if(right==tads[i+1]['left']){drawDashed(right, "r", false)};
            if(right!=tads[i+1]['left']){drawDashed(right, "r", true)};
        } else {
            drawDashed(right, "r", true)
        }
    }


    // Draw dashed line for chromosome end if necessary
    if (data.minimum['type']=='chromosome'){drawDashed(start_coord, "l", true);}
    if (data.maximum['type']=='chromosome'){drawDashed(end_coord, "r", true);}

    // Draw CNV
    canvas.append("line")
        .attr("x1", scale(data.cnv_start))
        .attr("y1", 145)
        .attr("x2", scale(data.cnv_end))
        .attr("y2", 145)
        .attr("stroke", "green")
        .attr("stroke-width", 6)
        .on("mouseover", function(){
            var start_label = canvas.append("text").attr("x", scale(data.cnv_start)).attr("y", 157).attr("font-size", 10).attr("text-anchor", "middle")
                .attr("font-weight", 550).attr("fill", "green").attr("class", "cnv-label").text(numberWithCommas(data.cnv_start));
            var end_label = canvas.append("text").attr("x", scale(data.cnv_end)).attr("y", 157).attr("font-size", 10).attr("text-anchor", "middle")
                .attr("font-weight", 550).attr("fill", "green").attr("class", "cnv-label").text(numberWithCommas(data.cnv_end));
        }).on("mouseout", function(){
            d3.selectAll(".cnv-label").remove();
        })

    var last_end_point = [0];
    var data_to_display = [];

    data.enhancers.forEach(function(enhancer){
        var line = canvas.append("line")
            .attr("x1", scale(enhancer.start))
            .attr("x2", function(){
                if (scale(enhancer.end)-scale(enhancer.start)>10){
                    return scale(enhancer.end);
                } else {
                    return scale(enhancer.end)+10;
                }
            })
            .attr("data-vista", enhancer.vista_element).attr("y1", 300).attr("y2", 300).attr("stroke", "purple").attr("stroke-width", 6)
            .attr("class", "enhancer")
            .on("mouseover", function(){
                canvas.append("text")
                    .text("Vista "+$(this).data("vista")).attr("text-anchor", "middle")
                    .attr("x", scale(enhancer.start))
                    .attr("y", 290)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select("#hoverText").remove()
            })

    })

    var genes = data.genes;
    for(var i = 0; i<genes.length; i++){
        var stroke_color = "blue";
        if (genes[i].phenotype_score > 0){stroke_color = "orange"};

        // End of gene rectangle
        var end_point = scale(genes[i].start)+10;
        if (scale(genes[i].end)>end_point){end_point = scale(genes[i].end);}

        var row = 0;
        var overlap = true;
        while(overlap){
            if (row >= last_end_point.length){
                last_end_point.push(end_point);
                overlap = false;
            }
            if (scale(genes[i].start) >= last_end_point[row] + 3){
                last_end_point[row] = end_point;
                overlap = false;
            }
            if (scale(genes[i].start) < last_end_point[row] + 3){
                    row += 1;
            }
        };

        data_to_display.push({
            "Name": genes[i].name,
            "Start": genes[i].start,
            "End": genes[i].end,
            "Number of matches": genes[i].phenotype_score,
            "Matches": genes[i].matches,
            "Phenotypes": genes[i].phenotypes,
        });

        // Draw the gene
        canvas.append("line")
            .attr("x1", scale(genes[i].start))
            .attr("y1", 165+row*11)
            .attr("x2", end_point)
            .attr("y2", 165+row*11)
            .attr("stroke", stroke_color)
            .attr("stroke-width", 10)
            .attr("data-name", genes[i].name)
            .attr("data-x1", scale(genes[i].start))
            .attr("data-stroke_color", stroke_color)
            .attr("data-gene_number", i)
            .on("mouseover", function(){
                d3.select(this)
                .attr("stroke", "black")
                canvas.append("text")
                    .text(this.getAttribute("data-name"))
                    .attr("x", this.getAttribute("data-x1"))
                    .attr("y", 165)
                    .attr("id", "hoverText")
                    .style("font-family", "Arial")
                    .style("font-weight", 700)
            })
            .on("mouseout", function(){
                d3.select(this)
                    .attr("stroke", this.getAttribute("data-stroke_color"))
                d3.select("#hoverText").remove()
            })
            .on("click", function(){
                //Clears all data from the Patient Data Display panel
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

})
