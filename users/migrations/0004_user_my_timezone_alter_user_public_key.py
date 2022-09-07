# Generated by Django 4.1 on 2022-09-02 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_send_stat_email_alter_user_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="my_timezone",
            field=models.SmallIntegerField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="public_key",
            field=models.CharField(db_index=True, default="0000000000", max_length=25),
        ),
    ]
