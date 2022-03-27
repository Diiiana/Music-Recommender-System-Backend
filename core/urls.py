from django.contrib import admin
from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('account.urls')),
    path('api/artists/', include('artist.urls')),
    path('api/songs/', include('song.urls')),
    path('api/tags/', include('tag.urls'))
]
