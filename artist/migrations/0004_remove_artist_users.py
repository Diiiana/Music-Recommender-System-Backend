# Generated by Django 3.2.12 on 2022-04-03 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0003_artist_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='users',
        ),
    ]
