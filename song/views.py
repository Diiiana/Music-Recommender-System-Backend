from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Song
from account.models import UserAccount
from .serializers import SongSerializer, ViewSongSerializer

@api_view(['GET'])
def get_songs(self):
    queryset = Song.objects.all()
    serializer_class = SongSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_song_by_id(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    return Response(ViewSongSerializer(song, many=False).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getUserSongs(request, user_id : int):
    user = UserAccount.objects.get(pk=user_id)
    return Response(ViewSongSerializer(user.liked_songs, many=True).data, status=status.HTTP_200_OK)
