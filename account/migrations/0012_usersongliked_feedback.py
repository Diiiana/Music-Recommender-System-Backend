# Generated by Django 3.2.12 on 2022-04-25 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20220424_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersongliked',
            name='feedback',
            field=models.IntegerField(default=-1),
        ),
    ]
