// import {MDCChipSet} from '@material/chips/chip-set';
import {MDCMenuSurface} from '@material/menu-surface';
import {MDCRipple} from '@material/ripple';
import {MDCSelect} from '@material/select';
import {MDCTopAppBar} from '@material/top-app-bar';
import {MDCTextField} from "@material/textfield";

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
