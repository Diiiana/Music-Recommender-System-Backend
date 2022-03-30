from django.http import HttpResponse
from rest_framework.decorators import api_view
from song.serializers import MainAttributesSerializer
from django.db import connection
import json
from song.models import Song
from .cf_mf_recommender import RecommenderCFMatrix 

@api_view(['POST'])
def get_cb_rec(request):
    similarities = []
    favoriteSongs = request.data.get('songs')
    print(favoriteSongs)
    c = connection.cursor()
    
    for song_id in favoriteSongs:
        c.execute('SELECT * FROM song_similarities(' + str(song_id) + ')')
        rows = c.fetchall()
        for s in rows:
            similarities.append(s[0])
    c.close()
    s = Song.objects.filter(pk__in=similarities)
    return HttpResponse(status=200, content=json.dumps(MainAttributesSerializer(s, many=True).data))

@api_view(['POST'])
def test_cf_mf(request):
    RecommenderCFMatrix()
    return HttpResponse(status=200)