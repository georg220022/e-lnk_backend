#Генераторы коротких ссылок
import random


class GeneratorShortCode():

    @staticmethod
    def for_postgresql() -> str:
        """
        data НЕ содержит буквы 'r' и 'R' (они для Redis-генератора кода)
        для облегчения определения
        в какой из БД искать данные.
        Тут генерируется код для базы PostgreSQL
        (для зарегестрированных юзеров).
        Поэтому у ссылок от зарегестрированных юзеров
        в ссылке гарантированно будет буква 'p'.
        """
        data = '123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS'
        random_p = random.randint(1, 9)
        new_url = ''
        for counter in range(10):
            new_url += data[random.randint(0, 59)]
            if counter == random_p:
                new_url += 'p'
        return new_url

    @staticmethod
    def for_redis() -> str:
        """
        data НЕ содержит буквы 'p' и 'P' (они для PostgreSQL-генератора кода)
        для облегчения определения
        в какой из БД искать данные.
        Тут генерируется код для NoSQL базы Redis
        (для не авторизованных юзеров).
        Поэтому у ссылок от не авторизованных юзеров
        в ссылке гарантированно будет буква 'r'
        """
        data = '1OA567890qwertyuioSDFGHJKLZXC234asdfghjklzxcvbnmQWERTYUIVBNM'
        random_r = random.randint(1, 9)
        new_url = ''
        for counter in range(10):
            new_url += data[random.randint(0, 59)]
            if counter == random_r:
                new_url += 'r'
        return new_url
