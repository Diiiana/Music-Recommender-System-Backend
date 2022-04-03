from django.urls import path
from .views import MyTokenObtainPairView, getUserProfile, getUsers, registerUser, resetPassword, changePassword

urlpatterns = [
    path('', getUsers, name='users'),

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', getUserProfile, name='users-profile'),
    path('register/', registerUser, name='register'),
    path('reset-password', resetPassword, name='reset-password'),
    path('change-password', changePassword, name='change-password'),
]