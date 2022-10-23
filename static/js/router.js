import user from './buisness/user.js';

import { LoadMainPage, LoadPanelPage, LoadSettingsPage } from './pages.js';
import { hidePreloader } from './handlers/preloader.js';

function router(route) {
	switch (route) {
		case '#/':
			document.title = 'E-lnk';
			LoadMainPage();
			break;
		case '#/panel':
			document.title = 'Панель управления | E-lnk';
			LoadPanelPage();
			break;
		case '#/settings':
			document.title = 'Настройки аккаунта | E-lnk';
			LoadSettingsPage();
			break;
	};
};

document.addEventListener('DOMContentLoaded', async () => {
	await user.refreshTokens();
	
	if (window.location.hash.length == 0) {
		window.location.hash = "#/";
	} else router(window.location.hash);
});

window.addEventListener('hashchange', () => {
	if (document.body.classList.contains('burger-menu-overlay')) {
	document.body.classList.remove('burger-menu-overlay');
	};

	router(window.location.hash);
});

document.addEventListener('readystatechange', () => {
	if (document.readyState === "complete") {
		hidePreloader();
	};
});

export default router;