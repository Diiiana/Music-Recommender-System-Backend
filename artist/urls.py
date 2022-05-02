from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_artists),
    path('music', views.get_music_for_user),
    path('latest-popular', views.get_latest_popular)
]