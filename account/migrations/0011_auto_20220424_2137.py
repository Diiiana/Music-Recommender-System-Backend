# Generated by Django 3.2.12 on 2022-04-24 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20220424_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersonghistory',
            name='timestamp',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='usersongliked',
            name='timestamp',
            field=models.DateField(auto_now_add=True),
        ),
    ]