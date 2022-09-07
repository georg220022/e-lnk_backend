# Generated by Django 3.2 on 2022-08-14 21:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "link_count",
                    models.IntegerField(default=0, verbose_name="количество ссылок"),
                ),
                (
                    "subs_type",
                    models.CharField(
                        choices=[
                            ("REG", "REGISTERED"),
                            ("BTEST", "BETA TESTER"),
                            ("MOD", "MODERATOR"),
                        ],
                        max_length=50,
                        verbose_name="тип подписки",
                    ),
                ),
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                (
                    "violations",
                    models.IntegerField(default=0, verbose_name="количество нарушений"),
                ),
                (
                    "trust",
                    models.BooleanField(
                        default=False, verbose_name="доверенный пользователь"
                    ),
                ),
                (
                    "username",
                    models.CharField(max_length=50, null=True, verbose_name="имя"),
                ),
                (
                    "company_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="компания"
                    ),
                ),
                ("email", models.EmailField(max_length=100, unique=True)),
                (
                    "is_active",
                    models.BooleanField(default=False, verbose_name="статус активации"),
                ),
                ("is_staff", models.BooleanField(default=False, verbose_name="админ")),
                (
                    "date_join",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="дата регистрации",
                    ),
                ),
                ("banned", models.BooleanField(default=False)),
                (
                    "public_key",
                    models.CharField(db_index=True, default=0, max_length=25),
                ),
                (
                    "trust_rating",
                    models.IntegerField(
                        default=100000, null=True, verbose_name="Рейтинг доверия"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
    ]
