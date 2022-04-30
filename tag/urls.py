from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_tags),
    path('user', views.get_artists_by_genres),
    path('popularity', views.getTagsByPopularity)
]
