import user from './user.js';
import router from '../router.js';
import { validateAuthFilledInput, validateEmptyInput, createJSONObjectFromInputs, sendRequest} from '../utils.js';

const LOGIN_API = 'api/v1/login';

let loginFormVars = {}; 
let l = loginFormVars;

function enableLoginForm() {
	l.loginForm = document.getElementById('login-form');
	l.loginFormInputs = l.loginForm.querySelectorAll('input');
	l.loginFormSubmitBtn = document.getElementById('login-submitBtn');

	l.loginForm.setAttribute('novalidate', true);

	l.loginFormInputs.forEach(input => {
		input.removeEventListener('blur', () => validateAuthFilledInput(input));
		input.removeEventListener('input', () => validateAuthFilledInput(input));
	});
	l.loginForm.removeEventListener('submit', submitLoginForm);

	l.loginFormInputs.forEach(input => {
		input.addEventListener('blur', () => validateAuthFilledInput(input));
		input.addEventListener('input', () => validateAuthFilledInput(input));
	});
	l.loginForm.addEventListener('submit', submitLoginForm);
};

async function submitLoginForm() {
	event.preventDefault();

	let isValid = false;

	let validatedInputs = Array.from(l.loginFormInputs).map(input => {
		let inputIsValid = validateAuthFilledInput(input) && validateEmptyInput(input);
		return inputIsValid;
	});

	isValid = validatedInputs.every(input => input === true);

	if (isValid) {
		let jsonForReq = createJSONObjectFromInputs(l.loginFormInputs);

		l.loginFormSubmitBtn.classList.add('loader');
		l.loginFormInputs.forEach((input) => input.setAttribute('disabled', 'disabled'));

		let json = await sendRequest(LOGIN_API, jsonForReq, false, true);

		if (json && json.access) {
			user.email = json.email;
			user.accessToken = json.access;

			document.querySelector('.modal--open')?.classList.remove('modal--open');
			document.querySelector('#body-section')?.classList.remove('lock');

			router('#/');
			
		} else if (json.error) {
			alert(json.error);
		} else {
			alert('Не получилось выполнить вход :( \nПожалуйста, попробуйте позже');
		};

		l.loginFormSubmitBtn.classList.remove('loader');
		l.loginFormInputs.forEach((input) => input.removeAttribute('disabled'));
		l.loginForm.reset();
	};
};


export default enableLoginForm;


