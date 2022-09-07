function burgerMenuEvent(event) {
	if (event.target.closest('.burger')) {
		event.target.classList.toggle('burger--active');
		document.querySelector('.header__nav')?.classList.toggle('burger-menu--active');
		document.body.classList.toggle('burger-menu-overlay');
	};

	if (event.target.closest('.nav__button') && document.querySelector('.burger')?.classList.contains('burger--active')) {
		document.querySelector('.burger')?.classList.remove('burger--active');
		document.querySelector('.header__nav')?.classList.remove('burger-menu--active');
		document.body.classList.remove('burger-menu-overlay');
	};

	if (event.target.closest('#body-section') && !event.target.matches('.burger') && !event.target.closest('.burger-menu--active')) {
		document.querySelector('.burger')?.classList.remove('burger--active');
		document.querySelector('.header__nav')?.classList.remove('burger-menu--active');
		document.body.classList.remove('burger-menu-overlay');
	};

	return;
};

export default burgerMenuEvent;