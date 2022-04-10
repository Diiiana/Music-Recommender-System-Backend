from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserAccountSerializer, UserSerializerWithToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import UserAccount
from tag.models import Tag
from artist.models import Artist
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection
import uuid


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        
        for k, v in serializer.items():
            data[k] = v
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def registerUser(request):
    data = request.data
    
    try:
        user = UserAccount.objects.create(
            user_name = data['user_name'],
            email = data['email'],
            password = make_password(data['password'])
            )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with this email already exists!'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user # authenticated user - data from token
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
        user = UserAccount.objects.all().filter(email=user_email['email']).first()
        token = str(user.id) + '/' + str(uuid.uuid4())
        subject = "Forget password link"
        message = f'Hello! \n Click on the link to reset your password \n http://localhost:3000/user/change-password/{token}'
        email_from = settings.EMAIL_HOST_USER
        recepient_list = [user_email['email']]
        send_mail(subject, message, email_from, recepient_list)
        return Response(token, status=200)
    except Exception as e:
        message = {'detail': 'Email Address not found!'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def changePassword(request):
    user_id = request.data.get('userId')
    new_password = request.data.get('password')
    user = UserAccount.objects.get(id=user_id)
    user.password = make_password(new_password)
    user.save()
    return Response(status=200)
