if (!document.cookie.match('cookie-consent=true')) {
	
	const template = `
	<div class="cookie-consent">
		<div class="cookie-consent__body">
			<p class="cookie-consent__text">Мы используем cookies</p>
			<button class="cookie-consent__button button--main">Хорошо</button>
		</div>
	</div>
`;

	let cookieElem = document.createElement('div');
	cookieElem.innerHTML = template;

	setTimeout(() => {
		document.body.append(cookieElem);
		
		let cookieBtn = document.querySelector('.cookie-consent__button');
		
		cookieBtn.addEventListener('click', hideCookieElem);
	}, 2000);

	function hideCookieElem(e) {
		document.cookie = 'cookie-consent=true; path=/; expires=Wen, 28 May 2098 00:28:00 GMT';
		e.target.removeEventListener('click', hideCookieElem);
		document.body.removeChild(cookieElem);
	};
};




