from django.db import models
from artist.models import Artist
from tag.models import Tag


class Song(models.Model):
    id = models.AutoField(primary_key=True)
    song_id = models.CharField(max_length=50, default=None)
    song_name = models.CharField(max_length=220)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, default=None)
    tag = models.TextField(max_length=200, default=None, null=True)
    release_date = models.CharField(max_length = 10, default=None)
    creation_date = models.DateField(default=None)
    duration = models.IntegerField(default=0)
    danceability = models.FloatField(default=0)
    acousticness = models.FloatField(default=0)
    instrumentalness = models.FloatField(default=0)
    valence = models.FloatField(default=0)
    energy = models.FloatField(default=0)
    speechiness = models.FloatField(default=0)
    image = models.BinaryField(blank=True, editable=True, null=True)
    url = models.TextField(blank=True, max_length = 200, null=True)
    spotify_uri = models.TextField(blank=True, max_length = 200, null=True)
    tags = models.ManyToManyField(Tag)
    
    class Meta:
        db_table = "song"  
