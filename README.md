## E-LNK.RU 
![Основная панель](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D0%9F%D0%B0%D0%BD%D0%B5%D0%BB%D1%8C_1.png)
#### Сервис сокращения ссылок с последующим сбором и обработкой статистики в реальном времени.

#### Что сервис делает:
-  Показывает с каких устройств переходят по ссылке
- В какое время и сколько было кликов по ссылке
- С каких ОС переходят по ссылке
- ТОП 10 стран из которых перешли по ссылке
- Статистика переходов за текущую неделю
- Ежедневная отправка подробного отчета по всем ссылкам за прошедшие сутки на почту
- Создание короткой ссылки
- Возможность установить пароль и/или лимит переходов по ссылке
- Ограничить время действия (ссылка будет доступна с выбранной даты и времени и/или до выбранной даты и времени)
с точностью до 1-й минуты
- Показывает повторные клики (переходы совершенные с одного устройства) 
- Создает QR код ссылки
- При рассчетах учитывает любой часовой пояс
- Быстрое создание ссылок на ozon, wildberries, aliexpress через добавление префикса 'ee' в начало ссылки
ПРИМЕР:
кликните на ссылку, и короткая ссылка автоматически скопируется вам в буфер обмена и вернет на страницу товара.
https://www.eeozon.ru/product/trusiki-podguzniki-mioki-razmer-l-9-14-kg-42-sht-622328422/?advert=ps8FCfaqISubkpc7gYy5k2ojQwLB2jcm0nffpnaJfY83OOCmB-LQKsW6qgZ69IhQ4RgwjS_6y5zKK66MyVi58aSA7kjVKLQA1xdxco-eFjsBEH3nv4ZMpz148EqlYw&sh=GjNv7whCug
- ###### ВАЖНО! Быстрое создание не поддерживает поддомены и доменные зоны отличные от .ru
***
#### Техническая реализация и подробности
- ```КЕШ-БУФЕР КЛИКОВ```: Каждый клик по ссылке собирает информацию о времени и устройстве пользователя в кеш, при достижении 1000 записей информация записывается в БД одним большим запросом.
- ```ДИНАМИЧЕСКИЙ TTL```: время жизни кешированных данных в зависимости от нагрузки на процессор сервера (от 10 сек до 1 часа, проверяется 1 раз в минуту)
- ```НЕТ ЛИШНИХ РАССЧЕТОВ```: При открытии панели пользователем производится единовременный рассчет данных с записью итогового JSON'a в кеш, так же удаляется информация по кликам из БД которая была подсчитана. Так же собирает и удаляет данные из "системы буфера кликов"(данные которые не успели попасть в БД). При последующих открытиях панели складывается старый + новый JSON, получается актуальная информация на текущий момент.
- ```ОПТИМИЗАЦИЯ РАССЧЕТОВ```: Рассчеты производятся во время открытия панели, если у пользователя появляется более 5000 не обработанных данных, во избежание подвисаний при обращении к панели - данные рассчитываются в фоновом режиме с последующим удалением подсчитанных данных (Celery task).
- ```ГОСТЕВОЙ РЕЖИМ```: Пользователям с неподтвержденной почтой доступны все действия на сайте, кроме создания ссылки (модифицированна библиотека simple-JWT)
- ```ОТЗЫВ JWT ТОКЕНОВ БЕЗ ЛИШНИХ ЗАПРОСОВ```: Поиск пользователя при аутентификации происходит по public_id(короткий код из 10 случайно сгенерированных симоволов) вместо стандатного поиска по неизменяемому int(id) пользователя в БД, при смене или сбросе пароля генерируется новый public_id, что автоматически сделает все старые токены не валидными БЕЗ использования White_list или Black_list. Во всех остальных случаях поиск пользователя выполняется по неизменяемому int(id)
- ```ОПТИМИЗИРОВАНЫ ORM ЗАПРОСЫ```: Не берем лишние данные из БД, не нужные в той или иной ситуации
- ```БЛОКИРУЮЩИЕ ФУНКЦИИ```: Вынесены в отдельные таски (рассылка почты, статистики, уведомлений)
- ```СЕРВЕРНАЯ СТАТИСТИКА```: За прошедший день отправляется статистика по 50 важным пунктам, например кто-то пытается через API удалить не свою ссылку или другие действия которые невозможно совершить через Fron-end. Рассылается в Telegram списку администраторов сайта, количество админов - любое.
- ```МОДУЛИ КЕШИРОВАНИЯ```: Самописная система CRUD кеша, при высокой нагрузке на сервер любые изменения в панели происходят через редактирование кеша, БД в подгрузке новых данных НЕ используется.
При открытии ссылки с паролем и попытке его подбора, ссылка кешируется во избежание множества обращений к БД
- ```САМООБСЛУЖИВАНИЕ```: Сервер настроен полностью на самообслуживание, все данные удаляются либо Celry task, либо при обращении к панели. В БД хранятся только сами ссылки. Ссылки от гостевых пользователей хранятся в Redis с настроенной политикой удаления lru т.е (при достижении лимита в 200 мб, будут удалены самые не используемые (стандартный инструмент Redis))
- ```АДМИН-ПАНЕЛЬ```: Полностью подготовленная админ-панель для работы администраторов
- ```2 НАГРУЗОЧНЫХ ТЕСТИРОВАНИЯ + Pytest```:

1) Средствами ```Locust```:
> 1.1) Авторизованные http запросы средний RPS 35 у самой "тяжелой" части сайта (анализ каждого клика в реальном времени с отображением в панели и использованием функционала сайта), 0 ошибок.  
> 1.2) Средний RPS 250 у самой "легкой" части сайта (открытие ссылок от гостевого юзера, без обработки данных по клику).  
2) Средствами ```django-shell```:  
Создано 100 000 000 записей циклом по 1 запросу (знаю что нельзя, но для теста самое оно).  
Скорость записи в БД варьировалась от 1500 до 3000 в секунду.  
> 2.1) 33м записей обработаны только средствами фоновых процессов (проверка работы обнаружения множества необработанных записей у юзера)  
> 2.2) 33м записей обработаны только средствами панели (проверка корректности удаления обработанных данных)  
> 2.3) 34м записей обработаны одновременно используя алгоритм работы панели и фоновую обработку информации (эмуляция большого количества запросов, когда пользователь пользуется панелью)  
3) ```Pytest```:  
> 3.1) Использвал простейшие тесты, что бы облегчить разработку обновлений.  
- ```ПРОЧЕЕ```: (Тротлинг + логгирование + права доступа + рассылки) выполняются стандартыми инструментами Django
 P.s Во время тестов сайт ОЧЕНЬ сильно лагал, но отобразил всю информацию без исключения.  
P.p.s Мой хостинг стоит 350 рублей, выжимал что мог ))))  

***
### Технологии:
##### Django 4, DRF, Redis, PostgresSQL, Docker, Python 3, Nginx, Gunicorn, Locust, Ubuntu-server, Celery, Pytest, Flower, Telegram API
![Карта проекта](https://github.com/georg220022/e-lnk_backend/blob/main/images/example.png)
***  
### О авторе и проекте:  

Telegram: https://t.me/georg2022bcknd
Email: info@e-lnk.ru
GitHub: georg220022  

Сервис содержит более 3500 строк python кода, на разработку ушло около 3-х месяцев.
При разработке проекта не следовал слепо принципам таким как RESTful или DRY, если в тех или иных моментах выгодно было их нарушить - нарушал.
Код сервиса рассчитан на большие нагрузки, корректность подсчета проверена "синтетическим" тестом, в данный момент все упирается в железо сервера, всего 1 ядро отвечает вообще за все :)  
***
### Другие скриншоты:
![Гостевая страница](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D1%81%D1%82%D0%B0%D1%80%D1%82.png)
***
![Статистика за текущую неделю](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D0%9F%D0%B0%D0%BD%D0%B5%D0%BB%D1%8C_%D0%B4%D0%BD%D0%B8_%D0%BD%D0%B5%D0%B4%D0%B5%D0%BB%D0%B8.png)
***
![Админ-панель](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D0%B0%D0%B4%D0%BC%D0%B8%D0%BD%D0%BA%D0%B0.png)
***
![Настройки](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B8.png)
***
![Пример ежедневного PDF отчета](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D0%BF%D0%B4%D1%84_%D0%BE%D1%82%D1%87%D0%B5%D1%82.png)
***
![Настройка ссылки](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D1%81%D0%BC%D0%B5%D0%BD%D0%B0_%D0%B8%D0%BC%D0%B5%D0%BD%D0%B8_%D0%B8_%D0%BF%D0%B0%D1%80%D0%BE%D0%BB%D1%8F.png)
***
![Добавление ссылки](https://github.com/georg220022/e-lnk_backend/blob/main/images/%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5%20%D1%81%D1%81%D1%8B%D0%BB%D0%BA%D0%B8.png)
