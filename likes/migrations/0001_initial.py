# Generated by Django 3.2.12 on 2022-03-27 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=50, null=True)),
                ('song_id', models.CharField(max_length=50)),
                ('liked', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'likes',
            },
        ),
    ]
