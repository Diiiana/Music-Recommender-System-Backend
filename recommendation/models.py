from django.db import models
from account.models import UserAccount
from song.models import Song


class UserSongRecommendation(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField(Song, default=None)

    class Meta:
        db_table = "recommendation"
