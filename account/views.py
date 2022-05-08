from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserAccountSerializer, UserSerializerWithToken, UserFavoritesSerializer, UserLikedSerializer, UserHistorySerializer, PlaylistSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import UserAccount, UserSongLiked, UserSongHistory, Playlist, UserFavorites
from song.models import Song
from song.serializers import ViewSongSerializer
from tag.models import Tag
from tag.serializers import TagSerializer
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.utils import timezone
from artist.serializers import ArtistSerializer
from artist.models import Artist
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
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def registerUser(request):
    data = request.data
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
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            if UserAccount.objects.filter(email=data['email']).first() is not None:
                message = {'detail': 'Email address already taken!'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request):
    user = UserAccount.objects.get(id=request.user.id)
    serializer = UserAccountSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserFavoriteArtistsAndGenres(request):
    user = UserAccount.objects.get(id=request.user.id)
    favorites = UserFavorites.objects.filter(user=user).first()
    return Response(UserFavoritesSerializer(favorites, many=False).data, status=status.HTTP_200_OK)


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
def getUserPreferences(request):
    user = UserAccount.objects.get(id=request.user.id)
    interaction = UserSongLiked.objects.filter(user=user).first()
    favorites = UserFavorites.objects.filter(user=user).first()
    if(interaction is not None and favorites.tags.count() > 0 is not None and favorites.artists.count() > 0 is not None):
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
    user_songs = UserSongLiked.objects.filter(user=request.user, feedback=1)
    return Response(UserLikedSerializer(user_songs, many=True).data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserChartData(request):
    value = UserSongLiked.objects.filter(user=request.user).values(
        'timestamp').annotate(activity=Count('timestamp')).order_by('timestamp')
    return Response(value, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserPlaylists(request):
    user = UserAccount.objects.get(id=request.user.id)
    playlists = Playlist.objects.filter(user=user)
    return Response(PlaylistSerializer(playlists, many=True).data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveUserPlaylists(request):
    name = request.data.get('playlistName')
    user = UserAccount.objects.get(id=request.user.id)
    Playlist.objects.create(name=name, user=user)
    playlists = Playlist.objects.filter(user=user)
    return Response(PlaylistSerializer(playlists, many=True).data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def savePlaylistSong(request, song_id: int):
    playlist_list = request.data.get('playlists')
    song = Song.objects.get(id=song_id)
    user = UserAccount.objects.get(id=request.user.id)
    for id in playlist_list:
        playlist = Playlist.objects.get(id=id, user=user)
        playlist.songs.add(song)
    playlists = Playlist.objects.filter(user=user)
    return Response(PlaylistSerializer(playlists, many=True).data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPlaylistById(request, id: int):
    user = UserAccount.objects.get(id=request.user.id)
    playlist = Playlist.objects.get(id=id, user=user)
    return Response(PlaylistSerializer(playlist, many=False).data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSongFromPlaylist(request, id: int, song_id: int):
    user = UserAccount.objects.get(id=request.user.id)
    playlist = Playlist.objects.get(id=id, user=user)
    song = Song.objects.get(id=song_id)
    playlist.songs.remove(song)
    return Response(PlaylistSerializer(playlist, many=False).data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUserPlaylist(request, id: int):
    user = UserAccount.objects.get(id=request.user.id)
    playlist = Playlist.objects.get(id=id, user=user)
    playlist.delete()
    playlists = Playlist.objects.filter(user=user)
    return Response(PlaylistSerializer(playlists, many=True).data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteArtistFromFavorite(request, id: int):
    user = UserAccount.objects.get(id=request.user.id)
    user_favorites = UserFavorites.objects.get(user=user)
    artist = Artist.objects.get(id=id)
    user_favorites.artists.remove(artist)
    artists = UserFavorites.objects.get(user=user).artists
    return Response(ArtistSerializer(artists, many=True).data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteTagFromFavorite(request, id: int):
    user = UserAccount.objects.get(id=request.user.id)
    user_favorites = UserFavorites.objects.get(user=user)
    tag = Tag.objects.get(id=id)
    user_favorites.tags.remove(tag)
    tags = UserFavorites.objects.get(user=user).tags
    return Response(TagSerializer(tags, many=True).data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveArtists(request):
    artists = request.data.get('artists')
    artists = Artist.objects.filter(id__in=artists)
    user_id = request.user.id
    user = UserAccount.objects.get(id=user_id)
    user_artists = UserFavorites.objects.get(user=user)
    if user_artists is None:
        user_favorite_artists = UserFavorites.objects.create(user=user)
        user_favorite_artists.artists.add(*artists)
    else:
        user_artists.artists.add(*artists)
    user_artists = UserFavorites.objects.get(user=user).artists
    return Response(ArtistSerializer(user_artists, many=True).data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveTags(request):
    tags = request.data.get('tags')
    tags = Tag.objects.filter(id__in=tags)
    user_id = request.user.id
    user = UserAccount.objects.get(id=user_id)
    user_tags = UserFavorites.objects.get(user=user)
    if user_tags is None:
        user_favorite_tags = UserFavorites.objects.create(user=user)
        user_favorite_tags.tags.add(*tags)
    else:
        user_tags.tags.add(*tags)
    user_tags = UserFavorites.objects.get(user=user).tags
    return Response(TagSerializer(user_tags, many=True).data, status=200)
