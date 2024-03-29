# Generated by Django 3.2.12 on 2022-04-24 06:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('song', '0001_initial'),
        ('account', '0008_usersongliked'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSongHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('song', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='song.song')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_song_history',
            },
        ),
    ]
