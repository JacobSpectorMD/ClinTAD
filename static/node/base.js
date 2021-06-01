// import {MDCChipSet} from '@material/chips/chip-set';
import {MDCRipple} from '@material/ripple';
import {MDCTopAppBar} from '@material/top-app-bar';

const topAppBarEl = document.querySelector('.mdc-top-app-bar');
const topAppBar = new MDCTopAppBar(topAppBarEl);

const buttonEls = document.querySelectorAll('.mdc-button');
buttonEls.forEach(function(buttonEl) {
    let buttonRipple = new MDCRipple(buttonEl);
})

// const chipSetEl = document.querySelector('.mdc-chip-set');
// const chipSet = new MDCChipSet(chipSetEl);