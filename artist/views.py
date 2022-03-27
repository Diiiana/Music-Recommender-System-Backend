from .models import Artist
from .serializers import ArtistSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.db import connection
from song.models import Song
from song.serializers import MainAttributesSerializer
import json


@api_view(['GET'])
def get_artists(self):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_artists_by_genres(request):
    genres = list(map(int, request.data.get('genres')))
    
    artists_nb = request.data.get('count')
    genres_nb = len(request.data.get('genres'))
    
    # count = int(artists_nb/genres_nb)
    cursor = connection.cursor()
    query = "SELECT * FROM get_artist_for_tags (ARRAY " + str(genres) + ")"
    cursor.execute(query)
    results = cursor.fetchall()

    return Response(results, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_music(request):
    selected_genres = request.data.get('genres')
    selected_artists = list(map(int, request.data.get('artists')))
    artists = str(selected_artists)
    
    cursor = connection.cursor()
    query = "SELECT * FROM get_music_for_artists (ARRAY " + artists + ")"
    cursor.execute(query)
    results = cursor.fetchall()
    songs = []
    for i in range(0, len(results)):
        songs.append(results[i][1])

    c = Song.objects.filter(id__in=songs)
    c = MainAttributesSerializer(c, many=True).data
    return HttpResponse(status=200, content=json.dumps(c))
