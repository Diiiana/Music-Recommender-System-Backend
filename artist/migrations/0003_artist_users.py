# Generated by Django 3.2.12 on 2022-04-03 16:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('artist', '0002_alter_artist_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
