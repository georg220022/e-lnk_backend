# Generated by Django 4.1 on 2022-10-02 06:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('elink_index', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='linkreguser',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_link', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='infolink',
            name='link_check',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='link_link', to='elink_index.linkreguser'),
        ),
        migrations.AddConstraint(
            model_name='linkreguser',
            constraint=models.UniqueConstraint(fields=('short_code',), name='unique_generate_link'),
        ),
    ]