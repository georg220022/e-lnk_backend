function modalsEvent(event) {
	if (event.target.closest('#body-section') && document.querySelector('.modal--open') && !event.target.closest('.modal__body')) {
		document.querySelector('.modal--open').classList.remove('modal--open');
		document.body.classList.remove('lock');
	};

	if (event.target.closest('.modal-button')) {
		let currentModalID = event.target.getAttribute('data-target');
		let currentModal = document.getElementById(currentModalID);

		currentModal?.classList.add('modal--open');
		document.body.classList.add('lock');
	};

	if (event.target.closest('.modal__close-button')) {
		document.querySelector('.modal--open').classList.remove('modal--open');
		document.body.classList.remove('lock');
	};
};

export default modalsEvent;