# Generated by Django 3.2.12 on 2022-03-27 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
