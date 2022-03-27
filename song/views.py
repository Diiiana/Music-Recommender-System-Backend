from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Song
from .serializers import SongSerializer

@api_view(['GET'])
def get_songs(self):
    queryset = Song.objects.all()
    serializer_class = SongSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_song_by_id(request, song_id):
    song = Song.objects.get(pk=song_id)
    return Response(SongSerializer(song, many=False).data, status=status.HTTP_200_OK)


