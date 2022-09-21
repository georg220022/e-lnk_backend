import django
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Вы не ввели Email")
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.subs_type = "REG"
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password):
        return self._create_user(email, password)

    def create_superuser(self, email, password):
        return self._create_user(email, password, is_staff=True, is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin):

    CHOICES = (
        ("REG", "REGISTERED"),
        ("BTEST", "BETA TESTER"),
        ("MOD", "MODERATOR"),
    )
    CHOICES_TIME_ZONE = (
        ("-12", "-12"),
        ("-11", "-11"),
        ("-10", "-10"),
        ("-9", "-9"),
        ("-8", "-8"),
        ("-7", "-7"),
        ("-6", "-6"),
        ("-5", "-5"),
        ("-4", "-4"),
        ("-3", "-3"),
        ("-2", "-2"),
        ("-1", "-1"),
        ("+0", "+0"),
        ("+1", "+1"),
        ("+2", "+2"),
        ("+3", "+3"),
        ("+4", "+4"),
        ("+5", "+5"),
        ("+6", "+6"),
        ("+7", "+7"),
        ("+8", "+8"),
        ("+9", "+9"),
        ("+10", "+10"),
        ("+11", "+11"),
        ("+12", "+12"),
    )
    link_count = models.IntegerField(default=0, verbose_name="количество ссылок")
    subs_type = models.CharField(
        choices=CHOICES, max_length=50, db_index=True, verbose_name="тип подписки"
    )
    id = models.AutoField(primary_key=True, unique=True)
    violations = models.IntegerField(default=0, verbose_name="количество нарушений")
    trust = models.BooleanField(default=False, verbose_name="доверенный пользователь")
    username = models.CharField(max_length=50, null=True, verbose_name="имя")
    company_name = models.CharField(max_length=100, null=True, verbose_name="компания")
    email = models.EmailField(max_length=100, unique=True)
    is_active = models.BooleanField(
        default=False, db_index=True, verbose_name="статус активации"
    )
    send_stat_email = models.BooleanField(
        default=False, db_index=True, verbose_name="Отправлять статистику"
    )
    my_timezone = models.CharField(
        max_length=3,
        default="+0",
        choices=CHOICES_TIME_ZONE,
        db_index=True,
        verbose_name="Смещение по UTC",
    )
    is_staff = models.BooleanField(default=False, verbose_name="админ")
    date_join = models.DateTimeField(
        default=django.utils.timezone.now, verbose_name="дата регистрации"
    )
    banned = models.BooleanField(default=False, verbose_name="Бан")
    public_key = models.CharField(max_length=25, db_index=True, default="0000000000")
    trust_rating = models.IntegerField(
        default=100000, verbose_name="Рейтинг доверия", null=True
    )
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["email"] # Список имён полей для Superuser

    objects = MyUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
