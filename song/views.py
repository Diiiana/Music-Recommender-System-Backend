from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Song
from account.models import UserSongHistory, UserAccount, UserSongLiked, UserSongComment
from account.serializers import UserSongCommentSerializer
from .serializers import SongSerializer, ViewSongSerializer, MainAttributesSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from django.db import connection
import numpy as np
import pandas as pd
import tensorflow as tf
import json


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
    check_processed = list(UserSongLiked.objects.filter(
        user=user).values_list('processed', flat=True))
    if check_processed.count(False) > 30:
        data = []
        songs = list(UserSongLiked.objects.filter(
            user=user, processed=False).values_list('song', flat=True))
        for song_id in songs:
            liked = UserSongLiked.objects.get(user=user, song=song_id)
            if liked is not None:
                data.append(liked.feedback)
            else:
                data.append(0)
            liked.processed = True
            liked.save()
        reconstructed_model = tf.keras.models.load_model("neural_model")
        reconstructed_model.fit([
            np.array([request.user.id]*len(songs)), np.array(songs)], pd.Series(data))

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
    check_processed = list(UserSongLiked.objects.filter(
        user=user).values_list('processed', flat=True))
    print(check_processed)
    if check_processed.count(False) > 30:
        data = []
        songs = list(UserSongLiked.objects.filter(
            user=user, processed=False).values_list('song', flat=True))
        for song_id in songs:
            liked = UserSongLiked.objects.get(user=user, song=song_id)
            if liked is not None:
                data.append(liked.feedback)
            else:
                data.append(0)
            liked.processed = True
            liked.save()
        reconstructed_model = tf.keras.models.load_model("neural_model")
        reconstructed_model.fit([
            np.array([request.user.id]*len(songs)), np.array(songs)], pd.Series(data))
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def searchForSong(request):
    value = request.data.get('value')
    c = connection.cursor()
    c.execute(
        "SELECT id, ts_rank(for_text, websearch_to_tsquery('" + value + "')) as rank FROM TF_IDF_VIEW_SEARCH_BAR ORDER BY rank DESC;")
    rows = c.fetchall()
    values = []
    for s in rows[:50]:
        values.append(s[0])
    s = Song.objects.filter(id__in=values)
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))
