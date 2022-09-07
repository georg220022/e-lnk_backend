import AirDatepicker from 'air-datepicker';
import localeRu from 'air-datepicker/locale/ru';

function enableDatepicker() {
	const dateOptions = {
		locale: localeRu,
		timepicker : true,
		position: 'top center',
		buttons: 'clear',
		isMobile: true,
		minDate: new Date,
	};

	let StartDate = new AirDatepicker('#link-start', dateOptions);
	let EndDate = new AirDatepicker('#link-end', dateOptions);
};

export default enableDatepicker;