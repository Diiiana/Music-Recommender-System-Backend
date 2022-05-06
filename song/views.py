from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Song
from account.models import UserSongHistory, UserAccount, UserSongLiked, UserSongComment
from account.serializers import UserSongCommentSerializer
from .serializers import SongSerializer, ViewSongSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def get_songs(self):
    queryset = Song.objects.all()
    serializer_class = SongSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_song_by_id(request, song_id: int):
    song = Song.objects.get(id=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    if not list(UserSongHistory.objects.filter(user=user, song=song).values_list('user', flat=True)):
        UserSongHistory.objects.create(user=user, song=song)
    like_value = UserSongLiked.objects.filter(user=user, song=song).values_list(
        'feedback', flat=True).first()
    if like_value is None:
        like_value = -1
    data = {'liked': like_value,
            'song': ViewSongSerializer(song, many=False).data}
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dislike_song_by_id_for_user(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    if UserSongLiked.objects.filter(user=user, song=song).exists():
        value = UserSongLiked.objects.get(user=user, song=song)
        value.feedback = 0
        value.save()
    else:
        UserSongLiked.objects.create(user=user, song=song, feedback=0)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def like_song_by_id_for_user(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    if UserSongLiked.objects.filter(user=user, song=song).exists():
        value = UserSongLiked.objects.get(user=user, song=song)
        value.feedback = 1
        value.save()
    else:
        UserSongLiked.objects.create(user=user, song=song, feedback=1)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSongComments(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    comments = UserSongComment.objects.filter(song=song)
    if comments is not None:
        return Response(UserSongCommentSerializer(comments, many=True).data, status.HTTP_200_OK)
    else:
        return Response(status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMySongComments(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    comments = UserSongComment.objects.filter(
        user=user, song=song).values('id')
    if comments is not None:
        return Response(comments, status.HTTP_200_OK)
    else:
        return Response(status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveNewComment(request, song_id: int):
    song = Song.objects.get(pk=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    comment = request.data.get('comment')
    UserSongComment.objects.create(user=user, song=song, comment=comment)
    return Response(UserSongCommentSerializer(UserSongComment.objects.filter(song=song), many=True).data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSongsByReleaseDate(request):
    songs = Song.objects.all().order_by('-release_date')[:50]
    return Response(ViewSongSerializer(songs, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSongsByGenre(request, genre_id: int):
    songs = Song.objects.filter(tags__id=genre_id)[:100]
    return Response(ViewSongSerializer(songs, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSongsByArtist(request, artist_id: int):
    songs = Song.objects.filter(artist__id=artist_id)[:100]
    return Response(ViewSongSerializer(songs, many=True).data, status=status.HTTP_200_OK)
