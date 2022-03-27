from django.contrib import admin
from django.urls import path
from account import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('account.urls')),
]
