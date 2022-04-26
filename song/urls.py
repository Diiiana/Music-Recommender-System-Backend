from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_songs),
    path('id/<int:song_id>', views.get_song_by_id),
    path('user-dislike/id/<int:song_id>', views.dislike_song_by_id_for_user),
    path('user-like/id/<int:song_id>', views.like_song_by_id_for_user),
]