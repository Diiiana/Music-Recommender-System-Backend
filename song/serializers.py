from django.forms import ImageField
from rest_framework import serializers
from .models import Song
from artist.serializers import ArtistSerializer

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = (
            'id', 'song_name', 'release_date', 'duration', 'danceability',
            'loudness', 'acousticness', 'instrumental', 'valence', 'energy', 'topic', 'image', 'url')
        
        
class RelevantAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'tag', 'danceability', 'loudness', 'acousticness', 'instrumental', 'valence', 'energy', 'topic')
        
    
class MainAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'artist', 'tag', 'song_name', 'image', 'url')
    artist = ArtistSerializer()
    image = ImageField()
    