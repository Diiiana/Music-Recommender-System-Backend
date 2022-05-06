from django.http import HttpResponse
from rest_framework.decorators import api_view
from song.serializers import MainAttributesSerializer
from django.db import connection
import json
import numpy as np
import tensorflow as tf
from song.models import Song
from account.models import UserAccount, UserSongLiked
from song.serializers import ViewSongSerializer
# from .lightfm_recommender import LightfmRecommender
# from .ncf_rec import NcfRecommender
from likes.models import Likes
import pandas as pd
from .models import UserSongRecommendation
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import tensorflow as tf


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSimilarSongs(request, id: int):
    similarities = []
    user_id = request.user.id
    user = UserAccount.objects.get(id=user_id)
    c = connection.cursor()
    c.execute('SELECT * FROM song_similarities(' + str(id) + ')')
    rows = c.fetchall()
    for s in rows:
        similarities.append(s[0])
    c.close()

    s = Song.objects.filter(pk__in=similarities)
    recommendations = UserSongRecommendation.objects.filter(user=user).first()
    if recommendations is not None:
        recommendations.songs.add(*s)
    else:
        object = UserSongRecommendation.objects.create(user=user)
        object.songs.set(s)
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))


@api_view(['POST'])
def get_cb_rec(request):
    similarities = []
    user_id = request.data.get('userId')
    songs_liked = request.data.get('songs')

    user = UserAccount.objects.get(id=user_id)
    song = Song.objects.all().filter(id__in=songs_liked)
    for s in song:
        if UserSongLiked.objects.filter(user=user, song=s).first() is None:
            UserSongLiked.objects.create(user=user, song=s, feedback=1)

    favoriteSongs = songs_liked[:5]
    c = connection.cursor()

    for song_id in favoriteSongs:
        c.execute('SELECT * FROM song_similarities(' + str(song_id) + ')')
        rows = c.fetchall()
        for s in rows:
            similarities.append(s[0])
    c.close()
    s = Song.objects.filter(pk__in=similarities)
    recommendations = UserSongRecommendation.objects.filter(user=user).first()
    if recommendations is not None:
        recommendations.songs.add(s)
    else:
        object = UserSongRecommendation.objects.create(user=user)
        object.songs.set(s)
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))


@api_view(['GET'])
def test_cf_mf(request):
    reconstructed_model = tf.keras.models.load_model("neural_model")
    reconstructed_model.fit([np.array([71]), np.array([3000])], pd.Series([1]))
    # tf.keras.utils.plot_model(
    #     reconstructed_model, to_file='model.png', show_shapes=True)

    # song_ids = Likes.objects.all().values_list('song_id', flat=True).distinct()

    # predictions = reconstructed_model.predict(
    #     [np.array([2]*len(song_ids), dtype=np.int64), np.array(song_ids, dtype=np.int64)])
    # l = np.array(predictions, dtype=np.float32).tolist()
    # l = sum(l, [])
    # song_prediction = np.array(list(zip(song_ids, l)), dtype=object)
    # song_prediction = song_prediction[song_prediction[:, 1].argsort()]
    # print(song_prediction[::-1][:10])

    # predictions = reconstructed_model.predict(
    #     [np.array([3]*len(song_ids), dtype=np.int64), np.array(song_ids, dtype=np.int64)])
    # l = np.array(predictions, dtype=np.float32).tolist()
    # l = sum(l, [])
    # song_prediction = np.array(list(zip(song_ids, l)), dtype=object)
    # song_prediction = song_prediction[song_prediction[:, 1].argsort()]
    # print(song_prediction[::-1][:10])

    # predictions = reconstructed_model2.predict(
    #     [np.array([3]*len(song_ids), dtype=np.int64), np.array(song_ids, dtype=np.int64)])
    # l = np.array(predictions, dtype=np.float32).tolist()
    # l = sum(l, [])
    # song_prediction = np.array(list(zip(song_ids, l)), dtype=object)[:100]
    # print(song_prediction)

    # predictions = reconstructed_model2.predict(
    #     [np.array([5]*len(song_ids), dtype=np.int64), np.array(song_ids, dtype=np.int64)])
    # l = np.array(predictions, dtype=np.float32).tolist()
    # l = sum(l, [])
    # song_prediction = np.array(list(zip(song_ids, l)), dtype=object)[:100]
    # print(song_prediction)
    # return HttpResponse(ViewSongSerializer(data, many=True).data, status=200)
    return HttpResponse(200)
