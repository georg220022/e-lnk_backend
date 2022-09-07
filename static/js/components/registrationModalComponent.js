const registrationModalComponent = () => {
	const template = `
		<div class="modal" id="registration-modal">
			<div class="modal__body">
				<div class="modal__head">
					<button class="modal__close-button"></button>
				</div>
				<div class="modal__content" id="registration-section">
					<form class="hero__form form" id="registration-form" action="#" method="post" autocomplete="off">
						<label class="form__label form__label--email" for="registration-email">
							<input class="form__input form__input--email" id="registration-email" type="email" name="email" placeholder="Введите e-mail" required>
							<span class="error-label"></span>
						</label>
						<label class="form__label form__label--password" for="registration-password">
							<input class="form__input form__input--password" id="registration-password" type="password" name="password" placeholder="Введите пароль" required/>
							<span class="error-label"></span>
						</label>
						<label class="form__label form__label--repeat-password" for="registration-repeat-password">
							<input class="form__input form__input--repeat-password" id="registration-repeat-password" type="password" name="repeat-password" placeholder="Повторите пароль" required/>
							<span class="error-label"></span>
						</label>
						<div class="form__checkbox-wrapper">
						<input class="form__input form__input--checkbox" type="checkbox" name="consent-checkbox" id="registration-consent-checkbox" value="consent-checkbox" required>
						<span class="error-label"></span>
						<label class="form__label form__label--checkbox" for="registration-consent-checkbox">Принимаю условия <a class="form__terms-link" href="#">обработки персональных данных</a>
						</label>
						</div>
						<button class="form__button form__button--submit button--main" id="registration-submitBtn" type="submit" name="submit">Зарегистрироваться</button>
					</form>
				</div>
			</div>
		</div>
	`;

	return template;
};

export default registrationModalComponent;




