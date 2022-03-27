from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_artists),
    path('genre', views.get_artists_by_genres),
    path('songs', views.get_music)
]