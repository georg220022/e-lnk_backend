import { copyTextToClipboard } from '../utils.js'

function copyToClipboardEvent(event) {
	if (event.target.closest('.copy-button')) {
		event.preventDefault();
		document.querySelector('.copy-button').classList.add('checkmark');

		copyTextToClipboard(event.target.closest('.form').querySelector('.short-link').value)
			.then(() => setTimeout(() => document.querySelector('.copy-button').classList.remove('checkmark'), 1000));
	};
};

export default copyToClipboardEvent;