from django.urls import path
from . import views

urlpatterns = [
     path('test', views.testUserPref, name='users'),
    path('', views.getUsers, name='users'),
    path('user', views.getUser, name='user'),
    path('login', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('preferences',
         views.getUserPreferences, name='users-preferences'),
    path('user/favorites', views.getUserFavoriteArtistsAndGenres, name='user-favorites'),
    path('profile', views.getUserProfile, name='users-profile'),
    path('playlists', views.getUserPlaylists, name='users-playlists'),
    path('playlists/view/<int:id>', views.getPlaylistById, name='users-playlist-id'),
    path('playlists/delete-song/<int:id>/<int:song_id>', views.deleteSongFromPlaylist, name='users-playlist-delete-song'),
    path('playlists/new', views.saveUserPlaylists, name='users-new-playlist'),
    path('playlists/save/<int:song_id>', views.savePlaylistSong, name='users-save-song-playlist'),
    path('history', views.getUserHistory, name='users-history'),
    path('liked', views.getUserLiked, name='users-liked'),
    path('chart', views.getUserChartData, name='users-chart'),
    path('register', views.registerUser, name='register'),
    path('reset-password', views.resetPassword, name='reset-password'),
    path('changePassword', views.changePassword, name='changePassword'),
    path('logout/blacklist', views.BlacklistTokenUpdateView.as_view(),
         name='blacklist'),
]
