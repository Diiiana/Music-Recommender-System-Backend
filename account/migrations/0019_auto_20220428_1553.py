# Generated by Django 3.2.12 on 2022-04-28 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_alter_usersongcomment_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='artists',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='tags',
        ),
    ]