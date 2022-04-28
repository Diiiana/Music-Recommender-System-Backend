from rest_framework import serializers
from account.models import UserAccount, UserSongLiked, UserSongHistory, UserSongComment, Playlist, UserFavorites
from rest_framework_simplejwt.tokens import RefreshToken
from tag.serializers import TagSerializer
from song.serializers import ViewSongSerializer
from artist.serializers import ArtistSerializer


class UserAccountSerializer(serializers.ModelSerializer):
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email', 'isAdmin']

    def get_isAdmin(self, obj):
        return obj.is_staff


class UserSerializerWithToken(UserAccountSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email', 'isAdmin', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email']


class UserPreferencesSerializer(serializers.ModelSerializer):
    tags = TagSerializer('tags', many=True)
    artists = ArtistSerializer('artists', many=False)

    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email', 'tags', 'artists']


class UserLikedSerializer(serializers.ModelSerializer):
    user = UserSerializer('user', many=False)
    song = ViewSongSerializer('song', many=False)

    class Meta:
        model = UserSongLiked
        fields = ['user', 'song', 'timestamp', 'feedback']


class UserHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer('user', many=False)
    song = ViewSongSerializer('song', many=False)

    class Meta:
        model = UserSongHistory
        fields = ['user', 'song', 'timestamp']


class UserSongCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer('user', many=False)
    song = ViewSongSerializer('song', many=False)

    class Meta:
        model = UserSongComment
        fields = ['id', 'user', 'song', 'timestamp', 'comment']


class PlaylistSerializer(serializers.ModelSerializer):
    user = UserSerializer('user', many=False)
    songs = ViewSongSerializer('song', many=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user', 'songs']


class UserFavoritesSerializer(serializers.ModelSerializer):
    user = UserSerializer('user', many=False)
    tags = TagSerializer('tags', many=True)
    artists = ArtistSerializer('artists', many=True)
    
    class Meta:
        model = UserFavorites
        fields = ['id', 'user', 'tags', 'artists']
