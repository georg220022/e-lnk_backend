import random


class GeneratorCode:
    @staticmethod
    def for_postgresql() -> str:
        """Генератор короткого кода для ссылки НЕ содержащей буквы r-R"""
        data = "123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS"
        random_p = random.randint(1, 9)
        new_url = ""
        for counter in range(10):
            new_url += data[random.randint(0, 59)]
            if counter == random_p:
                new_url += "p"
        return new_url

    @staticmethod
    def for_redis() -> str:
        """Генератор короткого кода для ссылки НЕ содержащей буквы p-P"""
        data = "1OA567890qwertyuioSDFGHJKLZXC234asdfghjklzxcvbnmQWERTYUIVBNM"
        random_r = random.randint(1, 9)
        new_url = ""
        for counter in range(10):
            new_url += data[random.randint(0, 59)]
            if counter == random_r:
                new_url += "r"
        return new_url

    @staticmethod
    def public_id() -> str:
        """Генерация публичного кода для пользователя, по нему авторизация JWT
        ищет пользователя, код меняется при смене пароля, что позволит деавторизовать
        любое устройство если данные браузера пользователя были украдены, можно сказать
        аналог отзываемых токенов без <белого списка> токенов, что позволяет при каждом обновлении
        refresh токена пользователем экономить 1 запрос в базу данных для проверки наличия или
        отсутствия токена в <белом списке>"""
        new_public_key = ""
        data = "123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS"
        for _ in range(10):
            new_public_key += data[random.randint(0, 59)]
        return new_public_key

    @staticmethod
    def reset_pass_key() -> str:
        pass_key = ""
        data = "123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS"
        for _ in range(100):
            pass_key += data[random.randint(0, 59)]
        return pass_key
