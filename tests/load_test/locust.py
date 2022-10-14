from locust import HttpUser, task, between

class TestMainFunc(HttpUser):
    """Нагрузочное тестирование основного функционала сайта"""
    def __init__(self, parent):
       super(TestMainFunc, self).__init__(parent)
       self.token = ""
       self.headers = {}

    wait_time = between(1, 2)

    # Добавил лимит ссылок авторизованному юзеру, тест не нужен
    """@task
    def create_link(self):
        # Создаем ссылку от юзера
        self.client.post("api/v1/links", json={"longLink": "http://georg-dev.ru/"}, headers={"Authorization": f'Bearer {self.token}'})"""

    @task
    def open_settings(self):
        # Открываем настройки
        self.client.get("api/v1/settings", headers={"Authorization": f'Bearer {self.token}'}) 

    @task
    def open_panel(self):
        # Открываем панель
        self.client.get("api/v1/panel", headers={"Authorization": f'Bearer {self.token}'})

    @task
    def open_non_statistic_link(self):
        # Короткий код созданной ссылки от гостевого юзера
        self.client.get("AQluGrsvbv1")

    @task
    def open_statistic_link(self):
        # Короткий код созданной ссылки от зарегестрированного юзера
        self.client.get("tnpP9tQ3q3J")

    def on_start(self):
        # Авторизуем каждого пользователя (бота locust'a)
        response = self.client.post("api/v1/login", json={"email":"Почта_пользователя", "password":"пароль_пользователя"})
        self.token = response.json()['access']