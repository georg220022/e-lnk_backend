const loggedUserHeaderComponent = (user, panelLink='<li class="nav__item"><a class="button--main" href="#/panel">Панель управления</a></li>',
  settingsLink='<li><a class="dropdown__link" href="#/settings">Настройки</a></li>') => {
	const template = `
    <nav class="nav header__nav">
      <ul class="nav__list">
        ${panelLink}
        <li class="nav__item">
          <div class="dropdown">
            <a class="dropdown__button nav__link" href="#">${user.email}</a>
            <ul class="dropdown__list">
              ${settingsLink}
              <li><a class="dropdown__link logout-link" href="#">Выйти</a></li>
            </ul>
          </div>
        </li>
      </ul>
    </nav>
    <button class="burger">
      <span class="burger__line"></span>
    </button>
  `;

	return template;
};

export default loggedUserHeaderComponent;

