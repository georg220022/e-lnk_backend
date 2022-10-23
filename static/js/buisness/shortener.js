import user from './user.js';
import { validateEmptyInput, createJSONObjectFromInputs, ruDateToISODate, sendRequest } from '../utils.js';

const SHORTENER_API = 'api/v1/links';

let shortenerVars = {}; 
let s = shortenerVars;

function enableShortener() {
	s.shortener = document.getElementById('shortener-form');
	s.allShortenerFields = s.shortener.querySelectorAll('input');
	s.shortenerInputs = Array.from(s.allShortenerFields).slice(0, -1);
	s.shortenerSubmitBtn = document.getElementById('shortener-submitBtn');
	s.longLink = document.getElementById('long-link');
	s.shortLink = document.getElementById('short-link');
	s.heroBody = document.querySelector('.hero__content');
	s.shortLinkWrapper = document.querySelector('.form__input-wrapper--short-link');
	s.qr = document.getElementById('qr');
	s.qrWrapper = document.querySelector('.qr-body');

	s.shortener.setAttribute('novalidate', true);

	s.shortenerInputs?.forEach(input => {
		input.removeEventListener('blur', () => validateShortenerFilledInput(input));
		input.removeEventListener('input', () => validateShortenerFilledInput(input));
	});
	s.shortener?.removeEventListener('submit', submitShortener);

	s.shortenerInputs?.forEach(input => {
		input.addEventListener('blur', () => validateShortenerFilledInput(input));
		input.addEventListener('input', () => validateShortenerFilledInput(input));
	});
	s.shortener?.addEventListener('submit', submitShortener);
};

async function submitShortener(event) {
	event.preventDefault();

	let isValid = false;

	let validatedInputs = s.shortenerInputs.map(input => {
		let inputIsValid = validateShortenerFilledInput(input);
		return inputIsValid;
	});

	isValid = validatedInputs.every(input => input === true) && validateEmptyInput(s.longLink);

	if (isValid) {
		let jsonObjectFromInputs = createJSONObjectFromInputs(s.shortenerInputs, 'input.value');
		let objFromInputs = JSON.parse(jsonObjectFromInputs);
		if (objFromInputs.linkLimit) { objFromInputs.linkLimit = +objFromInputs.linkLimit };
		if (objFromInputs.linkStartDate) { objFromInputs.linkStartDate = ruDateToISODate(objFromInputs.linkStartDate) };
		if (objFromInputs.linkEndDate) { objFromInputs.linkEndDate = ruDateToISODate(objFromInputs.linkEndDate) };
		let jsonForReq = JSON.stringify(objFromInputs);

		s.shortenerSubmitBtn.classList.add('loader');
		s.allShortenerFields.forEach(input => input.setAttribute('disabled', 'disabled'));

		let json = await sendRequest(SHORTENER_API, jsonForReq, user.accessToken);

		if (json && json.shortLink && json.qr) {
			s.shortLink.value = json.shortLink;
			s.qr.src = `data:image/jpg;base64,${json.qr}`;
			s.shortLinkWrapper.classList.add('open');
			s.qrWrapper.classList.add('open');
			s.heroBody?.classList.add('open');
		} else if (json && json.error) {
			alert(json.error);
		} else alert('Не получилось сократить ссылку :( \nПожалуйста, попробуйте позже');

		s.shortenerSubmitBtn.classList.remove('loader');
		s.allShortenerFields.forEach(input => input.removeAttribute('disabled'));
		s.shortenerInputs.forEach(input => input.value = '');
	};
};

function validateShortenerFilledInput(input) {
	if (input.value === '') return true;

	let inputCorrectCondition = null;
	let inputErrorText = null;

	switch (input.name) {
		case ('longLink'):
			const linkRegExp = /^((ftp|http|https):\/\/)?(www\.)?([A-Za-zА-Яа-я0-9]{1}[A-Za-zА-Яа-я0-9\-]*\.?)*\.{1}[A-Za-zА-Яа-я0-9-]{2,8}(\/([\w#!:.?+=&%@!\-\/])*)?/;
			let linkIsCorrect = linkRegExp.test(input.value) && input.value.at(-1) !== '.';
			let linkContainsElnk = input.value.includes('e-lnk.ru');
			inputCorrectCondition = linkIsCorrect && !linkContainsElnk;

			if (!linkIsCorrect) {
				inputErrorText = 'Введите корректный адрес ссылки';
			};
			if (linkContainsElnk) {
				inputErrorText = 'Это наша ссылка :) Введите другую';
			};
			break;
		case ('linkName'):
			inputCorrectCondition = input.value.length < 25;
			inputErrorText = 'Имя ссылки не может быть длинее 25 символов';
			break;
		case ('linkLimit'):
			if (!Boolean(Number(input.value))) input.value = '';
			if (input.value.at(-1) === ' ') input.value = '';
			inputCorrectCondition = true;
			inputErrorText = '';
			break;
		case ('linkPassword'):
			inputCorrectCondition = input.value.length < 16;
			inputErrorText = 'Пароль не может быть длинее 16 символов';
			break;
		case ('linkStartDate'):
			inputCorrectCondition = true;
			inputErrorText = '';
			break;
		case ('linkEndDate'):
			inputCorrectCondition = true;
			inputErrorText = '';
			break;
	};

	if (!inputCorrectCondition) {
		input.nextElementSibling.innerText = inputErrorText;
		input.classList.add('error-input');
		return false;
	} else {
		input.nextElementSibling.innerText = '';
		input.classList.remove('error-input');
		return true;
	};
};


export default enableShortener;