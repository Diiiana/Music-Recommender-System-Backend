from rest_framework import serializers
from account.models import UserAccount
from rest_framework_simplejwt.tokens import RefreshToken

class UserAccountSerializer(serializers.ModelSerializer):
    isAdmin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserAccount
        fields = ['id', 'user_name', 'email', 'isAdmin',]
    
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