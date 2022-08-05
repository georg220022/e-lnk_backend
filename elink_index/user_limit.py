class UserLimit:

    def create_link(request_user):
        if request_user.banned == False:
            if request_user.subs_type == 'REG':
                if request_user.link_count < 100:
                    return True
                return {'error': 'Лимит 100 ссылок, удалите не нужные ссылки, кстати, сейчас идет открытое бета-тестирование сайта, '+
                                  'напишите нам на почту и вам совершенно бесплатно увеличат лимит до 500, навсегда'}
            elif request_user.subs_type == 'BTEST':
                if request_user.link_count < 500:
                    return True
                return {'error': 'Для участников бета-тестирования лимит 500 ссылок'}
            elif request_user.subs_type == 'MOD':
                return True
        else:
            return {'error': 'Учетная запись заблокирована'}
        return {'error': 'Ошибка 0LvQuNC80LjRgtGL, отправьте этот код ' +
                         'на почту и опишите время получения этой ошибки ' +
                         'и получите подарок от нашей команды'}


