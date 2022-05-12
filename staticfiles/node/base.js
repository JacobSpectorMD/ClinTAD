import {MDCMenuSurface} from '@material/menu-surface';
import {MDCRipple} from '@material/ripple';
import {MDCSnackbar} from '@material/snackbar';
import {MDCTopAppBar} from '@material/top-app-bar';
import {MDCTextField} from "@material/textfield";
import {csrftoken} from "../js/utilities";

// Text field instantiation
const textFieldEls = document.querySelectorAll('.mdc-text-field');
textFieldEls.forEach(function(textFieldEl) {
    let textField = new MDCTextField(textFieldEl);
})

const topAppBarEl = document.querySelector('.mdc-top-app-bar');
const topAppBar = new MDCTopAppBar(topAppBarEl);
const main = document.querySelector('main');
topAppBar.setScrollTarget(main);

// Attach ripple to buttons
const buttonEls = document.querySelectorAll('.mdc-button');
buttonEls.forEach(function(buttonEl) {
    let buttonRipple = new MDCRipple(buttonEl);
})

// Settings Menu
const settingsTabEl = document.querySelector('#settings-button');
if (settingsTabEl){
    const settingsMenu = new MDCMenuSurface(document.querySelector('#settings-menu'));
    settingsTabEl.addEventListener('click', function(){
        if ($('#settings-menu').hasClass('mdc-menu-surface--open')) {
            settingsMenu.close();
        } else {
            const width = $('#settings-menu').width();
            var x = $('#settings-button').position().left + $('#settings-button').width() - width + 16;
            settingsMenu.setAbsolutePosition(x, 0);
            settingsMenu.open();
        }
    });
}

const snackbar = new MDCSnackbar(document.querySelector('.mdc-snackbar'));
snackbar.timeoutMs = -1;
if (announcement != false) {
    snackbar.open();
}

$(document).on('click', '.announcement button', function(){
    $.ajax({
        type: 'GET',
        url: '/set_announcement/',
        headers: {'X-CSRFToken': csrftoken},
        success: function() {},
    });
})

