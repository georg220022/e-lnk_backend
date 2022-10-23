const preloader = document.getElementById('preloader');

function showPreloader() {
	if (preloader?.classList.contains('preloader--hide')) {
		preloader.style.display = 'flex';
		preloader?.classList.remove('preloader--hide');
	}
};

function hidePreloader() {
	preloader?.classList.add('preloader--hide');
	setTimeout(() => preloader.style.display = 'none', 1000);
};

export { showPreloader, hidePreloader };
