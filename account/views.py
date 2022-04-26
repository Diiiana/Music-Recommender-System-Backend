from tkinter import N
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserAccountSerializer, UserSerializerWithToken, UserPreferencesSerializer, UserLikedSerializer, UserHistorySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import UserAccount, UserSongLiked, UserSongHistory
from tag.models import Tag
from artist.models import Artist
from song.models import Song
from song.serializers import ViewSongSerializer
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db.models import Count
from django.utils import timezone
import random
from rest_framework.views import APIView
from .email_send import EmailSender

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def registerUser(request):
    data = request.data
    print(data['user_name'], data['email'], data['password'])
    try:
        user = UserAccount.objects.create(
            user_name=data['user_name'],
            email=data['email'],
            password=make_password(data['password'])
        )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        if UserAccount.objects.filter(user_name=data['user_name']).first() is not None:
            message = {'detail': 'This username is already taken!'}
        else:
            if UserAccount.objects.filter(user_name=data['email']).first() is not None:
                message = {'detail': 'Email address already taken!'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserAccountSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = UserAccount.objects.all()
    serializer = UserAccountSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def resetPassword(request):
    user_email = request.data.get('email')
    try:
        user = UserAccount.objects.get(email=user_email)
        EmailSender(user_email).start()
        return Response(user.id, status=200)
    except Exception as e:
        message = {'detail': 'Email Address not found!'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def changePassword(request):
    user_id = request.data.get('userId')
    new_password = request.data.get('password')
    token = request.data.get('token')
    user = UserAccount.objects.get(id=user_id)
    if user.password_reset_token is None or user.password_reset_token != token:
        return Response({'message': 'Password reset token is invalid!'}, status=400)
    else:
        if user.password_reset_token_expiration < timezone.now():
            return Response({'message': 'Password reset token is expired!'}, status=400)
        else:
            user.password = make_password(new_password)
            user.save()
            return Response(status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserPreferences(request, user_id: int):
    user = UserAccount.objects.get(id=user_id)
    interaction = UserSongLiked.objects.filter(user=user)
    if(interaction is not None and user.tags.count() > 0 is not None and user.artists.count() > 0 is not None):
        user_songs = UserSongLiked.objects.filter(
            user=user).values_list('song', flat=True)
        return Response(ViewSongSerializer(Song.objects.filter(id__in=user_songs), many=True).data, status=200)
    else:
        return Response(status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserHistory(request):
    user_songs = UserSongHistory.objects.filter(user=request.user)
    return Response(UserHistorySerializer(user_songs, many=True).data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserLiked(request):
    user_songs = UserSongLiked.objects.filter(user=request.user)
    return Response(UserLikedSerializer(user_songs, many=True).data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserChartData(request):
    value = UserSongLiked.objects.filter(user=request.user).values(
        'timestamp').annotate(total=Count('timestamp')).order_by('total')
    return Response(value, status=200)
