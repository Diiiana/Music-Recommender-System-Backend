from .models import Tag
from .serializers import TagSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.models import UserAccount
from django.db import connection


@api_view(['GET'])
def get_tags(self):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_artists_by_genres(request):
    user_id = request.data.get('userId')
    genres = request.data.get('genres')
    user = UserAccount.objects.get(id=user_id)
    
    tags = Tag.objects.all().filter(id__in=genres)
    user.tags.add(*tags)
    
    user.save()
    
    results = list(map(int, genres))
    cursor = connection.cursor()
    query = "SELECT * FROM get_artist_for_tags (ARRAY " + str(results) + ", " + str(90) + ")"
    cursor.execute(query)
    results = cursor.fetchall()

    return Response(results, status=status.HTTP_200_OK)