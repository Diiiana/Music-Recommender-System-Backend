# Generated by Django 3.2.12 on 2022-04-28 13:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0001_initial'),
        ('artist', '0004_remove_artist_users'),
        ('account', '0019_auto_20220428_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavorites',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('artists', models.ManyToManyField(to='artist.Artist')),
                ('tags', models.ManyToManyField(to='tag.Tag')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_favorites',
            },
        ),
    ]
