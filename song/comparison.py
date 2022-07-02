from django.http import HttpResponse
from rest_framework.decorators import api_view
from numpy import *
from sklearn.metrics.pairwise import cosine_similarity
from django.db import connection
from song.models import Song
import numpy as np
import time
import concurrent.futures
from sparse_dot_topn import awesome_cossim_topn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from numpy.linalg import norm
import pandas as pd
from song.serializers import MainAttributesSerializer
import json

######################################### PROCESSESS ##################################################

@api_view(['POST'])
def test_dictionary_processes(request):
    favorites = request.data.get('songs')
            
    for array_songs in favorites:
        start = time.time()
        songs = list(Song.objects.values_list('danceability', 'acousticness', 'instrumentalness', 'valence', 'energy', 'speechiness'))
        split_value = len(songs)
            
        first_interval = int(split_value/4)
        second_interval = int(split_value/2)
        third_interval = int((3/4)*split_value)
        
        for id in array_songs:
            similarities = []
            intervals = [[id, songs[:first_interval]],
                        [id, songs[first_interval:second_interval]],
                        [id, songs[second_interval:third_interval]], 
                        [id, songs[third_interval:split_value]]]
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                similarities.append([data for data in executor.map(content_based_for_song_th, intervals)])
        
        duration = (time.time() - start)
        print("Time=", duration, "songs=", len(array_songs))
        
    return HttpResponse(status=200, content=similarities)


def content_based_for_song_th(data):
    id = data[0]
    songs_as_d = data[1]
    selected = Song.objects.get(pk=id)
    selected = [selected.danceability, selected.acousticness, selected.instrumentalness, selected.valence, selected.energy, selected.speechiness]
    similarities = []
    
    arr1 = np.array([selected])
    for i in range(0, len(songs_as_d)):
        arr2 = np.array([songs_as_d[i]]).astype(np.float32)
        num = norm(arr1[0])*norm(arr2[0])
        if num != 0:
            cos = dot(arr1[0], arr2[0])/num
            similarities.append([i, cos])
    
    similarities.sort(key=lambda row: row[2:], reverse=True)
    return similarities[:10]

######################################### P O S T G R E S Q L ###########################
@api_view(['POST'])
def test_postgres_impl(request):
    favoriteSongs = request.data.get('songs')
    for array_songs in favoriteSongs:
        start = time.time()
        
        similarities = []
        for id in array_songs:
            c = connection.cursor()
            c.execute('SELECT * FROM song_similarities(' + str(id) + ')')
            rows = c.fetchall()
            for s in rows:
                similarities.append(s[0])
            c.close()
        
        s = Song.objects.filter(pk__in=similarities)
        duration = (time.time() - start)
        print("Time=", duration, "songs=", len(array_songs))
    
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))


################################# D I C T I O N A R Y ###########################

@api_view(['POST'])
def test_dictionary(request):
    favoriteSongs = request.data.get('songs')
    for array_songs in favoriteSongs:
        similarities = []
        start = time.time()
        for id in array_songs:
            result = content_based_for_song_d(id)
            similarities.append(result)
        duration = (time.time() - start)
        print("Time=", duration, "songs=", len(array_songs))
    return HttpResponse(status=200, content=similarities)


def content_based_for_song_d(id):
    songs_as_dictionary = list(Song.objects.values_list('danceability', 
    'acousticness', 'instrumentalness', 'valence', 'energy', 
    'speechiness'))
    selected_song = Song.objects.get(pk=id)
    selected_song = [selected_song.danceability, selected_song.acousticness,
    selected_song.instrumentalness, selected_song.valence, selected_song.energy,
    selected_song.speechiness]
    
    similarities = []
    for item in range(1, len(songs_as_dictionary)):
        cos = cosine_similarity([selected_song], [songs_as_dictionary[item]])
        similarities.append([item, cos[0][0]])
        
    similarities.sort(key=lambda row: row[2:], reverse=True)
    return similarities[:10]


######################################################### TF-IDF COSSIM

@api_view(['POST'])
def test_tf_idf_cossim(request):
    favoriteSongs = request.data.get('songs')
    for array_songs in favoriteSongs:
        similarities = []
        
        start = time.time()
        for id in array_songs:
            qs = list(Song.objects.all().values('id', 'artist__name', 'tag'))
            dataset = pd.DataFrame(list(qs))
            
            given_song = dataset.loc[dataset['id'] == id]
            given_song = [given_song.iloc[0]['artist__name'] + ', ' + given_song.iloc[0]['tag']]
            dataset = dataset[dataset.id != id]

            dataset['text'] = dataset['artist__name'] + ', ' + dataset['tag']
            dataset = dataset['text'].tolist()

            song_text_fit = TfidfVectorizer()
            song_text_fit.fit(dataset)
            songs = song_text_fit.transform(dataset)
            song_fit = song_text_fit.transform(given_song)
            data = awesome_cossim_topn(songs, song_fit.T, 50, 0.1, True, 4, True)
            data = data.tocoo()
            songs_ids = data.col 
            for s in songs_ids:
                similarities.append(s)
        duration = (time.time() - start)
        print("Time=", duration, "songs=", len(array_songs))
            
    return HttpResponse(status=200, content=similarities)

######################################################### TF-IDF POSTGRESQL

@api_view(['POST'])
def test_tf_idf_postgresql(request):
    favoriteSongs = request.data.get('songs')
    for array_songs in favoriteSongs:
        similarities = []
        start = time.time()
        for id in array_songs:
            s = Song.objects.get(pk=id)
            s_text = s.tag + ', ' + s.artist.name
            c = connection.cursor()
            c.execute("SELECT t.id, t.tag_name, ts_rank(search_vector, websearch_to_tsquery('" + s_text + "')) as rank_v FROM TF_IDF_VIEW t ORDER BY rank_v DESC;")
            rows = c.fetchall()
            similarities.append(rows)
            c.close()

        duration = (time.time() - start)
        print("Time=", duration, "songs=", len(array_songs))
    return HttpResponse(status=200, content=similarities)