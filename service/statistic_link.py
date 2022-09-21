from typing import Dict


class StatLink:
    def per_24_hour(data, user_tz):
        """Соберем статистику за текущие 24 часа"""
        device: Dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        countrys: Dict = {}
        hour = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0,
            21: 0,
            22: 0,
            23: 0,
        }

        for objs in data:
            device[objs["device_id"]] += 1
            if objs["country"] in countrys:
                countrys[objs["country"]] += 1
            else:
                countrys[objs["country"]] = 1
            objs["device"] = device
            tz_key = int(objs["date_check"].strftime("%H")) + int(user_tz)
            if tz_key in hour.keys():
                hour[tz_key] += 1
            else:
                if tz_key > 23:
                    new_key = tz_key - 23
                else:
                    new_key = 23 + tz_key
                hour[new_key] += 1
        if len(countrys) == 0:
            countrys = {"Страны": 0}
        hour.update({24: 0}) # Фронтендер сказал добавить "24", что бы JS адекватно сработал
        return hour, device, countrys
