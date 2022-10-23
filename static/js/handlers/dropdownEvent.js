function dropdownEvent(event) {

	if (event.target.closest('.dropdown__button')) {
		event.target.nextElementSibling.classList.toggle("dropdown__list--visible");
	};

	if (event.target.closest('#body-section') && !event.target.matches('.dropdown__button')) {
		document.body.querySelector('.dropdown__button')?.nextElementSibling.classList.remove('dropdown__list--visible');
	};

	return;
};

export default dropdownEvent;