import {MDCDialog} from '@material/dialog';
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

export const snackbar = new MDCSnackbar(document.querySelector('.mdc-snackbar'));
snackbar.setTitle = function(title) {
    $(this.surfaceEl).find('.announcement-title').html(title);
}
snackbar.setText = function(text) {
    $(this.surfaceEl).find('.announcement-text').html(text);
}

export function showSnackbarError(jqXHR, textStatus, errorThrown) {
    let errorText = 'Something went wrong, please try again'
    if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
        errorText = jqXHR.responseJSON.error;
    }
    snackbar.setTitle('An Error Occurred');
    snackbar.setText(errorText);
    snackbar.timeoutMs = 5000;
    snackbar.open();
}

// Clears text, select, and checkbox fields
export function clearFields () {
    for (let i=0; i < arguments.length; i ++){
        let field = arguments[i];
        field.value = '';
        $(field.root).removeClass('mdc-text-field--invalid mdc-select--invalid');

        // Clear checkboxes in .mdc-form-field elements
        if ($(field.root) && $(field.root).hasClass('mdc-form-field')) {
            $(field.root).find('input').prop('checked', false);
        }
    }
}

const helpDialogElement = document.querySelector('.help-dialog');
if (helpDialogElement) {
   const helpDialog = new MDCDialog(helpDialogElement);
    $(document).on('click', '#help-button', function() {
        helpDialog.open();
    })
}
