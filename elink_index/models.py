from django.db import models

from users.models import User


class LinkRegUser(models.Model):
    # Автор
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owner_link",
        null=False,
        verbose_name="Автор",
    )
    # Изначальная ссылка
    long_link = models.TextField(
        max_length=5000, null=False, verbose_name="Длинная ссылка"
    )
    # короткий код от ссылки
    short_code = models.CharField(
        db_index=True, max_length=20, verbose_name="Короткий код"
    )
    # дата добавления
    date_add = models.DateTimeField(blank=True, verbose_name="Дата")
    # описание
    description = models.CharField(
        null=True, max_length=1000, blank=True, verbose_name="Имя/Описание"
    )
    # количество переходов по ссылке
    limited_link = models.IntegerField(default=-1, blank=True, verbose_name="Лимит")
    # пароль на ссылку
    secure_link = models.CharField(blank=True, max_length=16, verbose_name="Пароль")
    # с какой даты ссылка активна
    start_link = models.DateTimeField(blank=True, null=True, verbose_name="Начало")
    # дата остановки доступа к ссылке
    date_stop = models.DateTimeField(blank=True, null=True, verbose_name="Конец")
    # Сколько раз перешли по ссылке всего
    how_many_clicked = models.IntegerField(default=0, verbose_name="Переходов всего")
    # Повторные переходы
    again_how_many_clicked = models.IntegerField(
        default=0, verbose_name="Повторных переходов"
    )
    # Разрешить просмотр полной статистики всем людям !!!UPD будет доступно в след обновах
    public_stat_full = models.BooleanField(default=False, null=True)
    # Показывать ограниченную статистику всем людям !!!UPD будет доступно в след обновах
    public_stat_small = models.BooleanField(default=False, null=True)
    qr = models.TextField(null=True, verbose_name="QR код")

    class Meta:
        # verbose_name = 'Ссылки от зарегестрированных пользователей'
        verbose_name_plural = "Ссылки пользователей"
        ordering = ["-date_add"]
        constraints = [
            models.UniqueConstraint(fields=["short_code"], name="unique_generate_link")
        ]

    def __str__(self):
        return f"{self.short_code}, {self.author}"


class InfoLink(models.Model):
    # Дата просмотра ссылки
    date_check = models.DateTimeField(db_index=True, verbose_name="Дата")
    # Какая ссылка открыта
    link_check = models.ForeignKey(
        LinkRegUser, on_delete=models.CASCADE, related_name="link_link", null=False
    )
    # Из какой страны перешли по ссылке
    country = models.CharField(
        blank=True, max_length=1000, null=True, verbose_name="Страна"
    )
    # Устройство
    device_id = models.PositiveSmallIntegerField(verbose_name="Устройство")
