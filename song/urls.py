from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_songs),
    path('id/<int:song_id>', views.get_song_by_id),
]