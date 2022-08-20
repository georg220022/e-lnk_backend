const benefitsComponent = () => {
	const template = `
		<section class="benefits">
			<div class="container">
				<div class="benefits__body">
					<div class="benefits__illustration-img-wrapper">
						<picture>
							<source srcset="./img/benefits_illustration.webp" type="image/webp">
							<img class="benefits__pic" src="./img/benefits_illustration.png" alt="иллюстрация">
						</picture>
					</div>
					<div class="benefits__content">
						<h2 class="benefits__title ">Наши преимущеcтва:</h2>
						<ul class="benefits__list">
							<li class="benefits__list-item">С&nbsp;каких устройств переходят</li>
							<li class="benefits__list-item">В&nbsp;какие дни активность выше</li>
							<li class="benefits__list-item">Отправим вам статистику на&nbsp;почту или&nbsp;telegram</li>
							<li class="benefits__list-item">Полный контроль ваших клиентов</li>
						</ul>
						<button class="benefits__button button--main modal-button" data-target="registration-modal">Начать бесплатно</button>
					</div>
				</div>
			</div>
		</section>
  `;

	return template;
};

export default benefitsComponent;








