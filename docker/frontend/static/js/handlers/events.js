import burgerMenuEvent from './burgerMenuEvent.js';
import dropdownEvent from './dropdownEvent.js';
import modalsEvent from './modalsEvent.js';
import copyToClipboardEvent from './copyToClipboardEvent.js';
import logoutEvent from './logoutEvent.js';


document.addEventListener('click', (event) => {

	burgerMenuEvent(event);

	dropdownEvent(event);

	modalsEvent(event);

	copyToClipboardEvent(event);

	logoutEvent(event);
});