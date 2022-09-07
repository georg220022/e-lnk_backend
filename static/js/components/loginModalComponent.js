const loginModalComponent = () => {
	const template = `
	<div class="modal" id="login-modal">
		<div class="modal__body">
			<div class="modal__head">
				<button class="modal__close-button"></button>
			</div>
			<div class="modal__content" id="login-section">
				<form class="hero__form form" id="login-form" action="#" method="post" autocomplete="off">
					<label class="form__label form__label--email" for="login-email">
						<input class="form__input form__input--email" id="login-email" type="email" name="email" placeholder="Введите e-mail" required>
						<span class="error-label"></span>
					</label>
					<label class="form__label form__label--password" for="login-password">
						<input class="form__input form__input--password" id="login-password" type="password" name="password" placeholder="Введите пароль" required/>
						<span class="error-label"></span>
					</label>
					<button class="form__button form__button--submit button--main" id="login-submitBtn" type="submit" name="submit">Войти</button>
				</form>
			</div>
		</div>
	</div>
	`;

	return template;
};

export default loginModalComponent;




