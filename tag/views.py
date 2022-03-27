from .models import Tag
from .serializers import TagSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_tags(self):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)
