# Generated by Django 3.2.12 on 2022-04-26 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('song', '0001_initial'),
        ('account', '0014_playlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='songs',
            field=models.ManyToManyField(default=None, to='song.Song'),
        ),
    ]