# Generated by Django 4.1 on 2022-09-03 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "elink_index",
            "0004_alter_infolink_country_alter_infolink_device_id_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="linkreguser",
            name="qr",
            field=models.TextField(null=True),
        ),
    ]
