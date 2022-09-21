from elink_index.models import InfoLink, LinkRegUser
from personal_area.serializers import StatSerializer
from django.core.cache import cache
from .model_for_pdf import PDF
from django.db.models import Q


class StatCreate:
    """Запись данных в pdf файл"""
    def every_day_stat(usr) -> None:
        query_list = list(
            InfoLink.objects.select_related("link_check")
            .only("author_id")
            .filter(Q(link_check__author_id=int(usr[3])))
            .values()
        )  # .values_list()
        context = {
            "query_list": query_list,
            "action": "task_celery",
            "user_tz": int(usr[3]),
        }
        serializer = StatSerializer(
            LinkRegUser.objects.filter(author_id=int(usr[3])),
            context=context,
            many=True,
        )
        data_user = []
        for info in serializer.data:
            if info["linkName"] == "":
                info["linkName"] = "Название не заполнено"
            total = sum(info["statistics"]["clicks"].values())
            pc = info["statistics"]["clicks"]["pc"]
            phone = info["statistics"]["clicks"]["mobile"]
            other = info["statistics"]["clicks"]["other"]
            re_click = cache.get(f"statx_aclick_24_{info['linkId']}")
            if not re_click:
                re_click = 0
            one_lnk_stat = [
                "1",
                str(info["linkName"]),
                str(total),
                str(re_click),
                str(pc),
                str(phone),
                str(other),
            ]
            one_lnk_stat += [str(obj) for obj in info["statistics"]["hours"].values()]
            data_user.append(one_lnk_stat)
        start_list = []
        start = 0
        for _ in range(105):
            start += 39
            start_list.append(start)
        col_widths_2 = (84, 34, 168)
        col_widths = (
            5,
            50,
            16,
            13,
            9,
            12,
            13,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
            7,
        )
        col_names_2 = [
            "Общая информация",
            "Устройства",
            "Подробная статистика за 24 часа",
        ]
        col_names = [
            "№",
            "Название",
            "Всего кликов",
            "Повторных",
            "ПК",
            "Телефоны",
            "Неизвестно",
            "00",
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
        ]
        pdf = PDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.colored_table(
            col_names, data_user, col_widths, col_widths_2, col_names_2, start_list
        )
        pdf.output(f"pdf_storage/{usr[2]}.pdf")
