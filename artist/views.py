from .models import Artist
from .serializers import ArtistSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.db import connection
from song.models import Song
from account.models import UserAccount, UserFavorites
from song.serializers import MainAttributesSerializer
import json
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Count


@api_view(['GET'])
def get_artists(self):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_music_for_user(request):
    selected_artists = request.data.get('artists')
    user_id = request.data.get('userId')
    user = UserAccount.objects.get(id=user_id)
    artist = Artist.objects.filter(id__in=selected_artists)

    favorites = UserFavorites.objects.filter(user=user).first()
    if favorites is not None:
        favorites.artists.set(artist)
    else:
        object = UserFavorites.objects.create(user=user)
        object.artists.set(artist)
        object.save()

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_popular(request):
    data = Song.objects.values('artist', 'release_date').annotate(
        popularity=Count('artist__id')).values('artist__id', 'artist__name', 'popularity', 'release_date').order_by('-popularity', '-release_date')
    return Response(data, status=status.HTTP_200_OK)
