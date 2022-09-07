import random


class GeneratorCode:
    @staticmethod
    def for_postgresql() -> str:
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
        new_public_key = ""
        data = "123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS"
        for _ in range(10):
            new_public_key += data[random.randint(0, 59)]
        return new_public_key
