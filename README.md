## E-LNK.RU 
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
- ```ОТЗЫВ JWT ТОКЕНОВ БЕЗ ЛИШНИХ ЗАПРОСОВ```: Поиск пользователя при аутентификации происходит по public_id(короткий код из 10 случайно сгенерированных симоволов) вместо стандатного просто id пользователя в БД, при смене или сбросе пароля генерируется новый public_id, что автоматически сделает все старые токены не валидными БЕЗ использования White_list или Black_list
- ```ОПТИМИЗИРОВАНЫ ORM ЗАПРОСЫ```: Не берем лишние данные из БД, не нужные в той или иной ситуации
- ```БЛОКИРУЮЩИЕ ФУНКЦИИ```: Вынесены в отдельные таски (рассылка почты, статистики, уведомлений)
- ```СЕРВЕРНАЯ СТАТИСТИКА```: За прошедший день отправляется статистика по 50 важным пунктам, например кто-то пытается через API удалить не свою ссылку или другие действия которые невозможно совершить через Fron-end. Рассылается в Telegram списку администраторов сайта, количество админов - любое.
- ```МОДУЛИ КЕШИРОВАНИЯ```: Самописная система CRUD кеша, при высокой нагрузке на сервер любые изменения в панели происходят через редактирование кеша, БД в подгрузке новых данных НЕ используется.
При открытии ссылки с паролем и попытке его подбора, ссылка кешируется во избежание множества обращений к БД
- ```САМООБСЛУЖИВАНИЕ```: Сервер настроен полностью на самообслуживание, все данные удаляются либо Celry task, либо при обращении к панели. В БД хранятся только сами ссылки. Ссылки от гостевых пользователей хранятся в Redis с настроенной политикой удаления lru т.е (при достижении лимита в 200 мб, будут удалены самые не используемые (стандартный инструмент Redis))
- ```АДМИН-ПАНЕЛЬ```: Полностью подготовленная админ-панель для работы администраторов
- ```2 НАГРУЗОЧНЫХ ТЕСТИРОВАНИЯ + Pytest```:

1) Средствами ```Locust```: 
1.1) Авторизованные http запросы средний RPS 35 у самой "тяжелой" части сайта (анализ каждого клика в реальном времени с отображением в панели и использованием функционала сайта), 0 ошибок. 
1.2) Средний RPS 250 у самой "легкой" части сайта (открытие ссылок от гостевого юзера, без обработки данных по клику).
2) Средствами ```django-shell```:
Создано 100 000 000 записей циклом по 1 запросу (знаю что нельзя, но для теста самое оно).
Скорость записи в БД варьировалась от 1500 до 3000 в секунду.
2.1) 33м записей обработаны только средствами фоновых процессов (проверка работы обнаружения множества необработанных записей у юзера)
2.2) 33м записей обработаны только средствами панели (проверка корректности удаления обработанных данных)
2.3) 34м записей обработаны одновременно используя алгоритм работы панели и фоновую обработку информации (эмуляция большого количества запросов, когда пользователь пользуется панелью)
3) ```Pytest```:
3.1) Использвал простейшие тесты, что бы облегчить разработку обновлений.

 P.s Во время тестов сайт ОЧЕНЬ сильно лагал, но отобразил всю информацию без исключения.
P.p.s Мой хостинг стоит 350 рублей, выжимал что мог ))))
- ```ПРОЧЕЕ```: (Тротлинг + логгирование + права доступа + рассылки) выполняются стандартыми инструментами Django
***
### Технологии:
##### Django 4, DRF, Redis, PostgresSQL, Docker, Python 3, Nginx, Gunicorn, Locust, Ubuntu-server, Celery, Pytest
***
### Прочее
Сервис содержит более 3500 строк python кода, на разработку ушло около 3-х месяцев.
