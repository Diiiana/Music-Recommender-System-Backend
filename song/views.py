from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Song
from account.models import UserSongHistory, UserAccount, UserSongLiked
from .serializers import SongSerializer, ViewSongSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import json


@api_view(['GET'])
def get_songs(self):
    queryset = Song.objects.all()
    serializer_class = SongSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_song_by_id(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    if not list(UserSongHistory.objects.filter(user=user, song=song).values_list('user', flat=True)):
        UserSongHistory.objects.create(user=user, song=song)
    data = {'liked': UserSongLiked.objects.filter(user=user, song=song).values(
        'feedback').first(), 'song': ViewSongSerializer(song, many=False).data}
    return Response(data, status=status.HTTP_200_OK)
