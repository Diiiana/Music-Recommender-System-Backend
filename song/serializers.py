from django.forms import ImageField
from rest_framework import serializers
from .models import Song
from artist.serializers import ArtistSerializer
from tag.serializers import TagSerializer


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = (
            'id', 'song_name', 'release_date', 'duration', 'danceability',
            'speechiness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'image', 'url')


class RelevantAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'tag', 'danceability', 'speechiness',
                  'acousticness', 'instrumentalness', 'valence', 'energy')


class MainAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'artist', 'tag', 'song_name', 'image', 'url')
    artist = ArtistSerializer()
    image = ImageField()


class ViewSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'song_name', 'artist', 'tags', 'song_name',
                  'image', 'url', 'tag', 'release_date')
    tags = TagSerializer('tags', many=True)
    artist = ArtistSerializer()
    image = ImageField()
