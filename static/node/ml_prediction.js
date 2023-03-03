import {csrftoken} from "../js/utilities";

$(document).on('click', '#predict-button', function(){
        $.ajax({
            type: 'GET',
            headers: {'X-CSRFToken': csrftoken},
            data: {'coordinates': '', 'phenotypes': ''},
            url: '/single/predict/',
            success: function (response) {
                $('#pathogenicity-prediction').html(response.pathogenicity);
            },
    });
})