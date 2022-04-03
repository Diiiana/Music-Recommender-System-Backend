from django.http import HttpResponse
from rest_framework.decorators import api_view
from song.serializers import MainAttributesSerializer
from django.db import connection
import json
from song.models import Song
from account.models import UserAccount
# from .cf_mf_recommender import RecommenderCFMatrix 
# from .collab_recommendations import MatrixFactorization
# from .lightfm_recommender import LightfmRecommender
# from .from_kg import FinalClass


@api_view(['POST'])
def get_cb_rec(request):
    similarities = []
    user_email = request.data.get('userEmail')
    songs_liked = request.data.get('songs')  
    
    user = UserAccount.objects.get(email=user_email)
    song = Song.objects.all().filter(id__in=songs_liked)
    user.liked_songs.add(*song)
    user.save()
    
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

@api_view(['POST'])
def test_cf_mf(request):
    # RecommenderCFMatrix()
    # MatrixFactorization()
    # FinalClass()
    # LightfmRecommender()
    return HttpResponse(status=200)