import {MDCSelect} from '@material/select';
import {MDCTextField} from '@material/textfield';
console.log("comment");
const nameField = new MDCTextField(document.querySelector('#name-label'));
const emailField = new MDCTextField(document.querySelector('#email-label'));
const coordinatesField = new MDCTextField(document.querySelector('#coordinates-label'));
const phenotypeField = new MDCTextField(document.querySelector('#phenotypes-label'));
const commentsField = new MDCTextField(document.querySelector('#comments-label'));


//Get cookies from browser
function getCookie (name) {
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
    $(document).on('click', '#submit-data-button', function() {
        console.log("error")
        let data = {
            name: nameField.value,
            email: emailField.value,
            coordinates: coordinatesField.value,
            phenotype: phenotypeField.value,
            comments: commentsField.value,
        };
        // var formData = new FormData();
        // formData.append('Name: ', nameField.value);
        // formData.append('Email: ', emailField.value); //
        // formData.append('Coordinates: ', coordinatesField.value);
        // formData.append('Phenotype: ', phenotypeField.value);
        // formData.append('Comments: ', commentsField.value);
        // console.log(formData);

        const csrftoken = getCookie('csrftoken');

        $.ajax({
            type: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: data,
            url: '/single/submit_case/',
            success: function(response){
                console.log(response);
            },
        });
    })

    



// $(document).ready(function () {
//     if (coordinates) {
//         coordinatesField.value = coordinates;
//     }
    
//     if (phenotypes !== '') {
//         phenotypesField.value = phenotypes;
//     }
// })

// $(document).on('click', '#track-labels-button', function() {
//     $('.track-label').toggleClass('hidden');
// })

// $(document).on('click', '#statistics-button', function() {
//     if (!coordinates || !phenotypes) { return }
//     var url = `/single/statistics/?coordinates=${coordinates}&phenotypes=${phenotypes}`;
//     window.open(url, "_blank");
// })