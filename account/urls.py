from django.urls import path
from .views import MyTokenObtainPairView, getUserProfile, getUsers, registerUser, resetPassword, changePassword, getUserPreferences, getUserHistory, getUserLiked, getUserChartData

urlpatterns = [
    path('', getUsers, name='users'),

    path('login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('preferences/<int:user_id>',
         getUserPreferences, name='users-preferences'),
    path('profile', getUserProfile, name='users-profile'),
    path('history', getUserHistory, name='users-history'),
    path('liked', getUserLiked, name='users-liked'),
    path('chart', getUserChartData, name='users-chart'),
    path('register', registerUser, name='register'),
    path('reset-password', resetPassword, name='reset-password'),
    path('changePassword', changePassword, name='changePassword'),
]
