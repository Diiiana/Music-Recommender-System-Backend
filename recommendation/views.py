from django.http import HttpResponse
from rest_framework.decorators import api_view
from song.serializers import MainAttributesSerializer
from django.db import connection
import json
import numpy as np
import tensorflow as tf
from song.models import Song
from account.models import UserAccount, UserSongLiked
from tensorflow.keras.utils import plot_model
# from .lightfm_recommender import LightfmRecommender
# from .ncf_rec import NcfRecommender
# from .kerasmodel import KerasRecommender
from likes.models import Likes
import pandas as pd


@api_view(['POST'])
def get_cb_rec(request):
    similarities = []
    user_email = request.data.get('userEmail')
    songs_liked = request.data.get('songs')

    user = UserAccount.objects.get(id=user_email)
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
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))


def make_list(X):
    if isinstance(X, list):
        return X
    return [X]


def list_no_list(X):
    if len(X) == 1:
        return X[0]
    return X


@api_view(['GET'])
def test_cf_mf(request):
    # LightfmRecommender()
    reconstructed_model = tf.keras.models.load_model("neural_model")
    plot_model(reconstructed_model, to_file='model.png', show_shapes=True)

    song_ids = Likes.objects.all().values_list('song_id', flat=True).distinct()
    predictions = reconstructed_model.predict(
        [np.array([2]*len(song_ids), dtype=np.int64), np.array(song_ids, dtype=np.int64)])
    l = np.array(predictions, dtype=np.float32).tolist()
    l = sum(l, [])
    song_prediction = np.array(list(zip(song_ids, l)), dtype=object)
    return HttpResponse(song_prediction, status=200)
