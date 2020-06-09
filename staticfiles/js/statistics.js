function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function draw_statistics(){
    var svgs = d3.selectAll("svg");
    var text = svgs.append("text")
        .attr("x", $("#gene-matches").width()/2)
        .attr("y", "160")
        .attr("font-weight", "600")
        .attr("class", "loading")
        .attr("text-anchor", "middle")
        .text("Loading");

    var chromosome = $('[name="chromosome"]').val(),
        start = $('[name="start"]').val(),
        end = $('[name="end"]').val(),
        phenotypes = $('[name="phenotypes"]').val();
    var post_data = {'chromosome': chromosome, 'start': start, 'end': end, 'phenotypes': phenotypes};

    // Get data for actual variant
    var my_variant = {'gene_matches': null, 'hpo_matches': null, 'weighted_score': null};
    $.ajax({
        url: '/single/get_one_variant/',
        type: 'POST',
        headers: {"X-CSRFToken": csrftoken},
        data: post_data,
        success: function(d){
            data = JSON.parse(d);
            my_variant['gene_matches'] = data.gene_matches;
            my_variant['hpo_matches'] = data.hpo_matches;
            my_variant['weighted_score'] = data.weighted_score;
        }
    })

    var gene_matches = {},
        hpo_matches = {},
        weights = [];

    for (var i=0; i<=4; i++){
        // Get data for 500 random variants
        $.ajax({
            url: '/single/get_variants/',
            type: 'POST',
            headers: {"X-CSRFToken": csrftoken},
            data: post_data,
            success: function(d){
                d3.selectAll(".loading").remove();
                data = JSON.parse(d);
                data.forEach(function(variant){
                    weights.push(variant.weighted_score);
                    if (gene_matches[variant.gene_matches]==undefined){
                        gene_matches[variant.gene_matches] = 1;
                    } else {
                        gene_matches[variant.gene_matches] += 1;
                    }
                    if (hpo_matches[variant.hpo_matches]==undefined){
                        hpo_matches[variant.hpo_matches] = 1;
                    } else {
                        hpo_matches[variant.hpo_matches] += 1;
                    }
                })
                draw_graph("#gene-matches", 10, my_variant['gene_matches'], gene_matches);
                draw_graph("#hpo-matches", 15, my_variant['hpo_matches'], hpo_matches);
                draw_weights(my_variant['weighted_score'], weights);
            }
        })
    }
}

function draw_graph(svg_id, domain, my_matches, matches){
    var svg = d3.select(svg_id);
    svg.selectAll(".el").remove();
    var width = $(svg_id).width()-50;

    var x = d3.scale.linear()
        .domain([0, domain])
        .range([50, width]);

    var max_y = 0,
        ticks = 0;
    for (var score in matches){
        if (matches[score] > max_y){
            max_y = matches[score];
        }
    }

    var y = d3.scale.linear()
        .domain([0, max_y])
        .range([0, 250]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks($(svg_id).data("ticks"))
        .orient("bottom");

    var axis_g = svg.append("g")
        .attr("transform", "translate(20, 276)")
        .attr("class", "el")
        .call(xAxis);

    var x_label = svg.append("text")
        .attr("x", width/2)
        .attr("y", "315")
        .attr("font-size", "1.2em")
        .attr("font-weight", "550")
        .attr("text-anchor", "middle")
        .attr("class", "el")
        .text($(svg_id).data("label")+" (500 Similar Variants)");

    var circle = svg.append("circle")
        .attr("cx", x(my_matches)+20)
        .attr("cy", 290)
        .attr("r", "8")
        .style("fill", "none")
        .style("stroke", "red")
        .style("stroke-width", "2")
        .attr("class", "el");

    for (var score in matches){
        var bar = svg.append("rect")
            .attr("x", x(score))
            .attr("y", 275-y(matches[score]))
            .attr("width", "40")
            .attr("height", y(matches[score]))
            .attr("fill", "#A9CCE3")
            .attr("class", "el");

        var match_text = svg.append("text")
            .attr("x", x(score)+20)
            .attr("y", 274-y(matches[score]))
            .attr("text-anchor", "middle")
            .text(matches[score])
            .attr("class", "el");
    }
}

function draw_weights(my_weight, weights){
    var svg = d3.select('#weighted-scores');
    svg.selectAll('.el').remove();
    var width = $('#weighted-scores').width()-50;

    var x = d3.scale.linear()
        .domain(d3.extent(weights))
        .range([50, width]);

    var weight_bins = d3.layout.histogram()
        .bins(x.ticks(20))
        (weights);

    var my_weight_x = 0;
    weight_bins.forEach(function(bin){
        if (my_weight > bin.x && bin.x > my_weight_x){
            my_weight_x = bin.x;
        };
    })

    var y = d3.scale.linear()
        .domain([0, d3.max(weight_bins, d => d.y)])
        .range([0, 250]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks($('#weighted-scores').data("ticks"))
        .orient("bottom");

    var axis_g = svg.append("g")
        .attr("transform", "translate(20, 276)")
        .attr("class", "el")
        .call(xAxis);

    var x_label = svg.append("text")
        .attr("x", width/2)
        .attr("y", "315")
        .attr("font-size", "1.2em")
        .attr("font-weight", "550")
        .attr("text-anchor", "middle")
        .attr("class", "el")
        .text($('#weighted-scores').data("label")+" (500 Similar Variants)");

    var circle = svg.append("circle")
        .attr("cx", x(my_weight_x)+20)
        .attr("cy", 290)
        .attr("r", "12")
        .style("fill", "none")
        .style("stroke", "red")
        .style("stroke-width", "2")
        .attr("class", "el");

    for (var bin_no in weight_bins){
        var bin = weight_bins[bin_no];

        var bar = svg.append("rect")
            .attr("x", x(bin.x))
            .attr("y", function(){return 274-y(bin.y)})
            .attr("width", "40")
            .attr("height", function(){return y(bin.y)})
            .attr("class", "el")
            .attr("fill", "#A9CCE3");

        var text = svg.append("text")
            .attr("x", x(bin.x)+20)
            .attr("y", 273-y(bin.y))
            .attr("text-anchor", "middle")
            .text(function(){
                if (bin.y > 0) {return bin.y}
                else {return ''};
            })
            .attr("class", "el");
    }

//    var bar = svg.selectAll(".bar")
//        .data(weight_bins)
//        .enter()
//        .append("g")
//            .attr("class", "bar")
//            .attr("transform", function(d) {return "translate(" + x(d.x)+", 0)";});
//
//    bar.append("rect")
//        .attr("x", 0)
//        .attr("y", function(d){return 274-y(d.y)})
//        .attr("width", "40")
//        .attr("height", function(d) {return y(d.y);})
//        .attr("fill", "#A9CCE3");
//
//    bar.append("text")
//        .attr("x", 20)
//        .attr("y", function(d){return 264-y(d.y)})
//        .attr("text-anchor", "middle")
//        .attr("class", "el")
//        .text(function(d){
//            if (d.length > 0){return d.length}
//            else {return ''};
//        });
}

