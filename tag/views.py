from .models import Tag
from .serializers import TagSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.models import UserAccount, UserFavorites
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
from song.models import Song


@api_view(['GET'])
@permission_classes([AllowAny])
def get_tags(self):
    queryset = Tag.objects.all().order_by('name')
    tag_data = TagSerializer(queryset, many=True)
    return Response(tag_data.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tag_by_id(request, tag_id: int):
    tag = Tag.objects.get(id=tag_id)
    tag_data = TagSerializer(tag, many=False).data
    return Response(tag_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_artists_by_genres(request):
    user_id = request.data.get('userId')
    genres = request.data.get('genres')
    user = UserAccount.objects.get(id=user_id)
    tags = Tag.objects.all().filter(id__in=genres)

    favorites = UserFavorites.objects.filter(user=user).first()
    if favorites is not None:
        favorites.tags.set(tags)
    else:
        object = UserFavorites.objects.create(user=user)
        object.tags.set(tags)
        object.save()
    results = list(map(int, genres))
    cursor = connection.cursor()
    query = "SELECT * FROM get_artist_for_tags (ARRAY " + \
        str(results) + ", " + str(90) + ")"
    cursor.execute(query)
    results = cursor.fetchall()

    return Response(results, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTagsByPopularity(request):
    data = Song.objects.values('tags').annotate(
        popularity=Count('tags__id')).values('tags__id', 'tags__name', 'popularity').order_by('-popularity')
    return Response(data, status=status.HTTP_200_OK)
