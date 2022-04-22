from rest_framework import serializers
from account.models import UserAccount
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


class UserPreferencesSerializer(serializers.ModelSerializer):
    tags = TagSerializer('tags', many=True)
    liked_songs = ViewSongSerializer('liked_songs', many=True)
    artists = ArtistSerializer('artists', many=False)

    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email', 'tags', 'artists', 'liked_songs']
