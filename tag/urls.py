from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_tags),
    path('id/<int:tag_id>', views.get_tag_by_id),
    path('user', views.get_artists_by_genres),
    path('popularity', views.getTagsByPopularity)
]
