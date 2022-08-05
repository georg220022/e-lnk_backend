from tabnanny import verbose
from django.db import models
from users.models import User


class LinkRegUser(models.Model):
    # Автор
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='owner_link', null=False)
    # Изначальная ссылка
    long_link = models.TextField(db_index=True, max_length=5000, null=False)
    # короткий код от ссылки
    short_code = models.CharField(db_index=True, max_length=20)
    # дата добавления
    date_add = models.DateTimeField(blank=True)
    # описание
    description = models.CharField(null=True, max_length=1000, blank=True)
    # включить лимит по переходам
    #limit = models.BooleanField(null=False, default=0)
    # количество переходов по ссылке
    limited_link = models.IntegerField(default=-1,
                                               blank=True)
    # пароль на ссылку
    secure_link = models.CharField(blank=True, max_length=10)
    # с какой даты ссылка активна
    start_link = models.DateTimeField(blank=True, null=True)
    # дата остановки доступа к ссылке
    date_stop = models.DateTimeField(blank=True, null=True)
    # Сколько раз перешли по ссылке всего
    how_many_clicked = models.IntegerField(db_index=True, default=0)
    # Повторные переходы
    again_how_many_clicked = models.IntegerField(db_index=True, default=0)
    # Разрешить просмотр полной статистики всем людям
    public_stat_full = models.BooleanField(default=False, null=True)
    # Показывать ограниченную статистику всем людям
    public_stat_small = models.BooleanField(default=False, null=True)

    class Meta:
        #verbose_name = 'Ссылки от зарегестрированных пользователей'
        verbose_name_plural = 'Ссылки от зарегестрированных пользователей'
        ordering = ['date_add']
        constraints = [
            models.UniqueConstraint(fields=['short_code'],
                                    name='unique_generate_link')
            ]
    
    def __str__(self):
        return f'{self.short_code}, {self.author}'


class InfoLink(models.Model):
    # Дата просмотра ссылки
    date_check = models.DateTimeField(db_index=True)
    # Какая ссылка открыта
    link_check = models.ForeignKey(LinkRegUser, on_delete=models.CASCADE,
                                   related_name='link_link', null=False)
    # Из какой страны перешли по ссылке
    country_check_id = models.CharField(db_index=True, blank=True,
                                        max_length=1000, null=True)
    # Устройство
    device_id = models.CharField(max_length=20, db_index=True)
