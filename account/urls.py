from django.urls import path
from .views import MyTokenObtainPairView, getUserProfile, getUsers, registerUser

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', getUserProfile, name='users-profile'),
    path('', getUsers, name='users'),
    path('register/', registerUser, name='register'),
]