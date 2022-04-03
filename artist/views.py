from .models import Artist
from .serializers import ArtistSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.db import connection
from song.models import Song
from account.models import UserAccount
from song.serializers import MainAttributesSerializer
import json


@api_view(['GET'])
def get_artists(self):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def get_music_for_user(request):
    selected_artists = request.data.get('artists')
    user_email = request.data.get('userEmail')
    
    user = UserAccount.objects.get(email=user_email)
    artist = Artist.objects.filter(id__in=selected_artists)
    user.artists.add(*artist)
    user.save()
    
    selected_genres = user.tags
    selected_artists = list(map(int, selected_artists))
    artists = str(selected_artists)
    
    cursor = connection.cursor()
    query = "SELECT * FROM get_music_for_artists (ARRAY " + artists + ")"
    cursor.execute(query)
    
    results = cursor.fetchall()
    songs = []
    for i in range(0, len(results)):
        songs.append(results[i][0])

    c = Song.objects.filter(id__in=songs)
    c = MainAttributesSerializer(c, many=True).data
    return HttpResponse(status=200, content=json.dumps(c))