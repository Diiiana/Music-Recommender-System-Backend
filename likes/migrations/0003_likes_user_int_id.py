# Generated by Django 3.2.12 on 2022-05-03 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('likes', '0002_alter_likes_song_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='likes',
            name='user_int_id',
            field=models.IntegerField(default=0),
        ),
    ]
