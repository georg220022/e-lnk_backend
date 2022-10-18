const successRegistrationComponent = (email) => {
	const template = `
  <div class="success-registration">
      <h2 class="success-registration__title">Вы успешно зарегестрированы!</h2>
      <p class="success-registration__text">Чтобы начать пользоваться сервисом, перейдите по&nbsp;ссылке из&nbsp;письма в&nbsp;вашем почтовом ящике 
        <span class="success-registration__email">${email}</span>
      </p>
  </div>
  `;

	return template;
};

export default successRegistrationComponent;