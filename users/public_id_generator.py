import random


class GeneratorId:
    def public_id():
        new_public_key = ''
        data = '123456DFGHJKLZXCVBNM7890qwezxcvbnmQWETYUItyuiopasdfghjklOPAS'
        for _ in range(10):
            new_public_key += data[random.randint(0, 59)]
        return new_public_key
