from django.db import models # Подключаем работу с моделями
# Подключаем классы для создания пользователей
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Создаем класс менеджера пользователей
class MyUserManager(BaseUserManager):
    # Создаём метод для создания пользователя
    def _create_user(self, email, password, **extra_fields):
        # Проверяем есть ли Email
        if not email: 
            # Выводим сообщение в консоль
            raise ValueError("Вы не ввели Email")
        # Проверяем есть ли логин
        #if not username:
            # Выводим сообщение в консоль
            #raise ValueError("Вы не ввели Логин")
        # Делаем пользователя
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        
        user.subs_type = 'REG'
        # Сохраняем пароль
        user.set_password(password)
        # Сохраняем всё остальное
        user.save(using=self._db)
        # Возвращаем пользователя
        return user
    
    # Делаем метод для создание обычного пользователя
    def create_user(self, email, password):
        # Возвращаем нового созданного пользователя
        return self._create_user(email, password)

    # Делаем метод для создание админа сайта
    def create_superuser(self, email, password):
        # Возвращаем нового созданного админа
        return self._create_user(email, password, is_staff=True, is_superuser=True)

# Создаём класс User
class User(AbstractBaseUser, PermissionsMixin):

    CHOICES = (
        ('REG', 'REGISTERED'),
        ('BTEST', 'BETA TESTER'),
        ('MOD', 'MODERATOR'),
    )
    link_count = models.IntegerField(default=0, verbose_name='количество ссылок')
    subs_type = models.CharField(choices=CHOICES, max_length=50, verbose_name='тип подписки')
    id = models.AutoField(primary_key=True, unique=True) # Идентификатор
    violations = models.IntegerField(default=0, verbose_name='количество нарушений')
    trust = models.BooleanField(default=False, verbose_name='доверенный пользователь') # Стандартно зарегестрированный пользователь - доверия нет
    username = models.CharField(max_length=50, null=True, verbose_name='имя') # Логин
    company_name = models.CharField(max_length=100, null=True, verbose_name='компания')
    email = models.EmailField(max_length=100, unique=True) # Email
    is_active = models.BooleanField(default=False, verbose_name='статус активации') # Статус активации
    is_staff = models.BooleanField(default=False, verbose_name='админ') # Статус админа
    date_join = models.DateTimeField(default=timezone.now(), verbose_name='дата регистрации')
    banned = models.BooleanField(default=False) #Банхаммер
    public_key = models.CharField(max_length=25, db_index=True, default=0000000000)
    #limit_link = models.PositiveIntegerField(default=1000) # Сколько всего ссылок можно создать
    USERNAME_FIELD = 'email' # Идентификатор для обращения
    #REQUIRED_FIELDS = ['email'] # Список имён полей для Superuser
 
    objects = MyUserManager() # Добавляем методы класса MyUserManager

    # Метод для отображения в админ панели
    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'