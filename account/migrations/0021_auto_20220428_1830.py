# Generated by Django 3.2.12 on 2022-04-28 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0004_remove_artist_users'),
        ('tag', '0001_initial'),
        ('account', '0020_userfavorites'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='artists',
            field=models.ManyToManyField(to='artist.Artist'),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='tags',
            field=models.ManyToManyField(to='tag.Tag'),
        ),
        migrations.DeleteModel(
            name='UserFavorites',
        ),
    ]
