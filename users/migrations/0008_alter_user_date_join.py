# Generated by Django 3.2 on 2022-08-03 02:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_date_join'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_join',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 3, 2, 26, 28, 921422, tzinfo=utc), verbose_name='дата регистрации'),
        ),
    ]
