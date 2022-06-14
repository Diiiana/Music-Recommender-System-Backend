from django.urls import path
from . import views
from . import comparison

urlpatterns = [
    path('', views.get_songs),
    path('id/<int:song_id>', views.get_song_by_id),
    path('user-dislike/id/<int:song_id>', views.dislike_song_by_id_for_user),
    path('user-like/id/<int:song_id>', views.like_song_by_id_for_user),
    path('comments/<int:song_id>', views.getSongComments),
    path('comments/user/<int:song_id>', views.getMySongComments),
    path('comments/post/<int:song_id>', views.saveNewComment),
    path('by-date', views.getSongsByReleaseDate),
    path('genre/<int:genre_id>', views.getSongsByGenre),
    path('artist/<int:artist_id>', views.getSongsByArtist),
    path('search', views.searchForSong),
    
    # test cosine
    path('test_dictionary', comparison.test_dictionary),
    path('test_dictionary_processes', comparison.test_dictionary_processes),
    path('test_postgres_impl', comparison.test_postgres_impl),
    
    # test tfidf
    path('test_tf_idf_python', comparison.test_tf_idf_cossim),
    path('test_tf_idf_postgres', comparison.test_tf_idf_postgresql),
]
