# Generated by Django 3.2.12 on 2022-06-23 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_auto_20220428_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersongliked',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
