import router from '../router.js';
import { sendRequest } from '../utils.js';

const REFRESH_API = 'api/v1/refresh';
const LOGOUT_API = 'api/v1/logout';

let user = {
	email: null,
	accessToken: null,

	refreshTokens: async function() {
		const refreshTokensRequestOptions = {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json;charset=UTF-8',
			},
		};

		try {
			let response = await fetch(REFRESH_API, refreshTokensRequestOptions);

			if (!response.ok) {
				this.logout();
				throw (`Токен не валиден(ответ сервера: ${response.status})`); //ВРЕМЕННАЯ СТРОЧКА ДЛЯ ОТЛАДКИ
			};

			let json = await response.json();
			console.log('Полученный json (refresh_request):'); //ВРЕМЕННАЯ СТРОЧКА ДЛЯ ОТЛАДКИ
			console.log(json); //ВРЕМЕННАЯ СТРОЧКА ДЛЯ ОТЛАДКИ

			if (json.access) {
				this.accessToken = json.access;
				this.email = json.email;
				return true;
			};
		} catch (error) {
			console.error('ошибка при рефреше (refresh_request): ' + error); //ВРЕМЕННАЯ СТРОЧКА ДЛЯ ОТЛАДКИ
		};
	},
	
	logout: async function() {
		try {
			await sendRequest(LOGOUT_API, '', false, true);
			this.accessToken = null;
			this.email = null;
			router('#/');
		} catch (error) {
			console.error('ошибка при логауте: ' + error); //ВРЕМЕННАЯ СТРОЧКА ДЛЯ ОТЛАДКИ
		};
	},
};

export default user;