# Generated by Django 3.2.12 on 2022-04-27 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_alter_playlist_songs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]