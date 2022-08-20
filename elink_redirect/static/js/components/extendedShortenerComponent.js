const extendedShortenerComponent = () => {
	const template = `
	<div class="logged-hero__body">
		<div class="hero__content">
			<form class="logged-hero__form form" id="shortener-form" action="#" method="post" autocomplete="off">
				<div class="form__input-wrapper form__input-wrapper--long-link">
					<label class="form__label form__label--long-link" for="long-link">
						<input class="form__input form__input--long-link" id="long-link" type="url" name="longLink" placeholder="Ссылка для сокращения" required>
						<span class="error-label"></span>
					</label>
					<button class="form__button shortener-button shortener-button--submit" id="shortener-submitBtn" type="submit" name="submit">
					<svg width="25" height="23" viewBox="0 0 25 23" xmlns="http://www.w3.org/2000/svg">
						<path d="M10.25 5.17677C10.25 4.1529 9.94942 3.15203 9.38628 2.30071C8.82314 1.4494 8.02272 0.785877 7.08625 0.39406C6.14978 0.00224309 5.11932 -0.100274 4.12516 0.0994724C3.13101 0.299219 2.21782 0.792259 1.50108 1.51624C0.784336 2.24023 0.296227 3.16264 0.0984777 4.16683C-0.0992715 5.17103 0.00222053 6.2119 0.39012 7.15783C0.778019 8.10376 1.4349 8.91226 2.2777 9.48109C3.12051 10.0499 4.11137 10.3535 5.125 10.3535C6.40389 10.3503 7.63483 9.86154 8.57361 8.98429L11.1111 11.351L11.1278 11.3636L11.1222 11.3678L8.57222 13.743C7.63417 12.8655 6.40354 12.3767 5.125 12.3737C4.11137 12.3737 3.12051 12.6773 2.2777 13.2462C1.4349 13.815 0.778019 14.6235 0.39012 15.5694C0.00222053 16.5154 -0.0992715 17.5562 0.0984777 18.5604C0.296227 19.5646 0.784336 20.487 1.50108 21.211C2.21782 21.935 3.13101 22.4281 4.12516 22.6278C5.11932 22.8275 6.14978 22.725 7.08625 22.3332C8.02272 21.9414 8.82314 21.2779 9.38628 20.4266C9.94942 19.5752 10.25 18.5744 10.25 17.5505C10.25 17.1338 10.1889 16.734 10.0958 16.3468L14.0458 13.5536L19.7778 17.8535C22.85 20.0267 25 16.9234 25 16.9234L10.0958 6.38047C10.1875 5.99327 10.25 5.59343 10.25 5.17677ZM5.125 7.70202C4.7967 7.70202 4.47161 7.6367 4.16829 7.5098C3.86498 7.38289 3.58938 7.19688 3.35723 6.96239C3.12509 6.7279 2.94094 6.44952 2.8153 6.14314C2.68967 5.83676 2.625 5.50839 2.625 5.17677C2.625 4.84515 2.68967 4.51677 2.8153 4.2104C2.94094 3.90402 3.12509 3.62564 3.35723 3.39115C3.58938 3.15665 3.86498 2.97065 4.16829 2.84374C4.47161 2.71683 4.7967 2.65152 5.125 2.65152C5.78804 2.65152 6.42393 2.91757 6.89277 3.39115C7.36161 3.86472 7.625 4.50703 7.625 5.17677C7.625 5.84651 7.36161 6.48881 6.89277 6.96239C6.42393 7.43597 5.78804 7.70202 5.125 7.70202ZM5.125 20.0758C4.46196 20.0758 3.82608 19.8097 3.35723 19.3361C2.88839 18.8625 2.625 18.2202 2.625 17.5505C2.625 16.8808 2.88839 16.2385 3.35723 15.7649C3.82608 15.2913 4.46196 15.0252 5.125 15.0252C5.78804 15.0252 6.42393 15.2913 6.89277 15.7649C7.36161 16.2385 7.625 16.8808 7.625 17.5505C7.625 18.2202 7.36161 18.8625 6.89277 19.3361C6.42393 19.8097 5.78804 20.0758 5.125 20.0758ZM25 5.80528C25 5.80528 22.85 2.70202 19.7778 4.87514L15.3264 8.01066L18.5958 10.3227L25 5.80528Z"/>
					</svg>
					</button>
				</div>
				<div class="form__optional-inputs">
					<label class="form__label form__label--link-name" for="link-name">
						<input class="form__input form__input--link-name" id="link-name" type="text" name="linkName" placeholder="Имя ссылки">
						<span class="error-label"></span>
					</label>
					<label class="form__label form__label--link-limit" for="link-limit">
						<input class="form__input form__input--link-limit" id="link-limit" type="text" name="linkLimit" placeholder="Лимит переходов">
						<span class="error-label"></span>
					</label>
					<label class="form__label form__label--link-password" for="link-password">
						<input class="form__input form__input--link-password" id="link-password" type="password" name="linkPassword" placeholder="Пароль">
						<span class="error-label"></span>
					</label>					
					<label class="form__label form__label--link-start" for="link-start">
						<input class="form__input form__input--link-start" id="link-start" type="text" name="linkStartDate" placeholder="Начало действия">
						<span class="error-label"></span>
					</label>
					<label class="form__label form__label--link-end" for="link-end">
						<input class="form__input form__input--link-end" id="link-end" type="text" name="linkEndDate" placeholder="Конец действия">
						<span class="error-label"></span>
					</label>
				</div>
				<div class="form__input-wrapper form__input-wrapper--short-link">
					<h2 class="logged-hero__short-link-title visually-hidden">Ваша короткая ссылка:</h2>
					<label class="form__label form__label--short-link" for="short-link">
						<input class="form__input form__input--short-link short-link" id="short-link" type="url" name="shortLink" placeholder="Результат" readonly>
					</label>
					<button class="form__button shortener-button shortener-button--copy copy-button">
					<svg width="21" height="26" viewBox="0 0 21 26" xmlns="http://www.w3.org/2000/svg">
						<path d="M11.8125 0H1.3125C0.964403 0 0.630564 0.136964 0.384422 0.380761C0.138281 0.624558 0 0.955218 0 1.3V16.9C0 17.2448 0.138281 17.5754 0.384422 17.8192C0.630564 18.063 0.964403 18.2 1.3125 18.2H7.875V20.8H10.5V18.2H7.87631V15.6H10.5V13H7.875V15.6H2.625V2.6H10.5V7.8H13.125V1.3C13.125 0.955218 12.9867 0.624558 12.7406 0.380761C12.4944 0.136964 12.1606 0 11.8125 0V0ZM7.875 9.1V10.4H10.5V7.8H9.1875C8.8394 7.8 8.50556 7.93696 8.25942 8.18076C8.01328 8.42456 7.875 8.75522 7.875 9.1ZM13.125 26H15.75V23.4H13.125V26ZM13.125 10.4H15.75V7.8H13.125V10.4ZM7.875 24.7C7.875 25.0448 8.01328 25.3754 8.25942 25.6192C8.50556 25.863 8.8394 26 9.1875 26H10.5V23.4H7.875V24.7ZM19.6875 7.8H18.375V10.4H21V9.1C21 8.75522 20.8617 8.42456 20.6156 8.18076C20.3694 7.93696 20.0356 7.8 19.6875 7.8ZM18.375 26H19.6875C20.0356 26 20.3694 25.863 20.6156 25.6192C20.8617 25.3754 21 25.0448 21 24.7V23.4H18.375V26ZM18.375 15.6H21V13H18.375V15.6ZM18.375 20.8H21V18.2H18.375V20.8Z"/>
					</svg>
					</button>
				</div>
				<div class="logged-hero__qr-body qr-body">
					<h2 class="qr-body__qr-title visually-hidden">QR-код вашей ссылки:</h2>
					<div class="qr-img-wrapper">
						<img class="qr-body__qr-img qr-img" id="qr" src="./img/qr.png" alt="QR-код">
					</div>
				</div>
			</div>
		</div>
	</form>
  `;

	return template;
};

export default extendedShortenerComponent;
