# Generated by Django 3.2.12 on 2022-04-03 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('song', '0001_initial'),
        ('account', '0004_useraccount_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='liked_songs',
            field=models.ManyToManyField(to='song.Song'),
        ),
    ]