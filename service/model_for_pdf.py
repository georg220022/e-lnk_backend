from fpdf import FPDF
from datetime import timedelta
from django.core.cache import cache


class PDF(FPDF):
    """Модель(скелет) PDF документа для статистики за прошедший день"""

    yesterday = cache.get("dt_now") - timedelta(hours=1)
    num_day = (yesterday).isoweekday()
    day_week_data = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среду",
        4: "Четверг",
        5: "Пятницу",
        6: "Субботу",
        7: "Воскресенье",
    }
    day_week = day_week_data[num_day]
    yesterday = yesterday.strftime("%Y-%m-%d")

    def set_title(
        self,
        headings: list,
        rows: list,
        col_widths: tuple,
        col_widths_2: tuple,
        col_names_2: list,
    ) -> None:
        self.set_font("roboto_black", "", 7)
        self.set_fill_color(61, 150, 229)
        self.set_text_color(255)
        self.set_draw_color(0)
        self.set_line_width(0.1)
        for col_width_2, heading_2 in zip(col_widths_2, col_names_2):
            self.cell(col_width_2, 4, heading_2, border=1, align="C", fill=True)
        self.ln()
        self.set_fill_color(61, 150, 229)
        self.set_text_color(255)
        self.set_draw_color(0)
        self.set_line_width(0.1)
        self.set_font("roboto_black", "", 6)
        for col_width, heading in zip(col_widths, headings):
            self.cell(col_width, 3, heading, border=1, align="C", fill=True)
        self.ln()

    def colored_table(
        self,
        headings: list,
        rows: list,
        col_widths: tuple,
        col_width_2: tuple,
        col_names_2: list,
        start_list: list,
    ) -> None:
        self.set_title(headings, rows, col_widths, col_width_2, col_names_2)
        self.set_font("roboto_black", "", 6)
        self.set_fill_color(224, 235, 255)
        self.set_text_color(0)
        fill = False
        counter = 1
        for cnt in rows:
            if counter in start_list:
                self.ln(1)
                self.add_font(
                    "roboto_black", "", "static/service/fonts/roboto_black.ttf"
                )
                self.set_font("roboto_black", "", 8)
                self.cell(
                    0,
                    10,
                    f"Статистика за {self.day_week} {self.yesterday}",
                    border=0,
                    align="C",
                )
                self.ln(1)
                self.set_title(headings, rows, col_widths, col_width_2, col_names_2)
                self.set_font("roboto_black", "", 6)
                self.set_fill_color(224, 235, 255)
                self.set_text_color(0)
                fill = False
            self.set_draw_color(0, 80, 180)
            self.cell(col_widths[0], 4, str(counter), border=1, align="C", fill=fill)
            for int_obj_1 in range(1, 9):
                self.cell(
                    col_widths[int_obj_1],
                    4,
                    cnt[int_obj_1],
                    border=1,
                    align="C",
                    fill=fill,
                )
            for int_obj_2 in range(9, 31):
                self.cell(
                    col_widths[7], 4, cnt[int_obj_2], border=1, align="C", fill=fill
                )
            self.ln()
            fill = not fill
            counter += 1
        self.cell(31, 0, "", "T")

    def header(self) -> None:
        self.add_font("roboto_black", "", "static/service/fonts/roboto_black.ttf")
        self.set_font("roboto_black", "", 8)
        self.image("static/service/img/e-lnk-logo.png", 10, 6, 50)
        self.cell(
            0,
            10,
            f"Статистика за {self.day_week} {self.yesterday}",
            border=0,
            align="C",
        )
        self.ln(15)

    def footer(self) -> None:
        self.cell(31, 0, "", "L")
        self.set_y(-5)
        self.cell(0, 0, f"Страница {self.page_no()} из {{nb}}", align="C")
