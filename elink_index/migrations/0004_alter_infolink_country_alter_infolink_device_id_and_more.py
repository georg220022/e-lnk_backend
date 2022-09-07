# Generated by Django 4.1 on 2022-08-25 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("elink_index", "0003_auto_20220816_1410"),
    ]

    operations = [
        migrations.AlterField(
            model_name="infolink",
            name="country",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="infolink",
            name="device_id",
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="linkreguser",
            name="again_how_many_clicked",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="linkreguser",
            name="how_many_clicked",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="linkreguser",
            name="long_link",
            field=models.TextField(max_length=5000),
        ),
    ]