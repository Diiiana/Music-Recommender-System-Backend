from django.db import models


class Likes(models.Model):
    user_id = models.CharField(max_length=50, null=True)
    song_id = models.IntegerField(default=0)
    liked = models.IntegerField(default=0)
    
    class Meta:
        db_table = "likes"