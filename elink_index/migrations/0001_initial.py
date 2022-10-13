# Generated by Django 4.1 on 2022-10-02 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InfoLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_check",
                    models.DateTimeField(db_index=True, verbose_name="Дата"),
                ),
                (
                    "country",
                    models.CharField(
                        blank=True, max_length=1000, null=True, verbose_name="Страна"
                    ),
                ),
                (
                    "device_id",
                    models.PositiveSmallIntegerField(verbose_name="Устройство"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LinkRegUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "long_link",
                    models.TextField(max_length=5000, verbose_name="Длинная ссылка"),
                ),
                (
                    "short_code",
                    models.CharField(
                        db_index=True, max_length=20, verbose_name="Короткий код"
                    ),
                ),
                ("date_add", models.DateTimeField(blank=True, verbose_name="Дата")),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Имя/Описание",
                    ),
                ),
                (
                    "limited_link",
                    models.IntegerField(blank=True, default=-1, verbose_name="Лимит"),
                ),
                (
                    "secure_link",
                    models.CharField(blank=True, max_length=10, verbose_name="Пароль"),
                ),
                (
                    "start_link",
                    models.DateTimeField(blank=True, null=True, verbose_name="Начало"),
                ),
                (
                    "date_stop",
                    models.DateTimeField(blank=True, null=True, verbose_name="Конец"),
                ),
                (
                    "how_many_clicked",
                    models.IntegerField(default=0, verbose_name="Переходов всего"),
                ),
                (
                    "again_how_many_clicked",
                    models.IntegerField(default=0, verbose_name="Повторных переходов"),
                ),
                ("public_stat_full", models.BooleanField(default=False, null=True)),
                ("public_stat_small", models.BooleanField(default=False, null=True)),
                ("qr", models.TextField(null=True, verbose_name="QR код")),
            ],
            options={
                "verbose_name_plural": "Ссылки пользователей",
                "ordering": ["-date_add"],
            },
        ),
    ]
