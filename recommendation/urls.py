from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cb_rec),
    path('cf_mf', views.get_cf_mf),
    path('similar/<int:id>', views.getSimilarSongs)
]