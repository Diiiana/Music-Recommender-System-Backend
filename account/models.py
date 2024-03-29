from django.db import models
from tag.models import Tag
from song.models import Song
from artist.models import Artist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, password, **other_fields)

    def create_user(self, email, user_name, password, tags, artists, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          tags=tags, artists=artists, **other_fields)
        user.set_password(password)
        user.save()
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email'), unique=True)
    user_name = models.CharField(max_length=100, unique=True)
    password_reset_token = models.CharField(
        max_length=100, unique=True, null=True)
    password_reset_token_expiration = models.DateTimeField(
        auto_now_add=True, null=True)

    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_name


class UserSongLiked(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    feedback = models.IntegerField(default=-1)
    processed = models.BooleanField(default=False)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "user_song_liked"
        unique_together = ('user', 'song')


class UserSongHistory(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "user_song_history"
        unique_together = ('user', 'song')


class UserSongComment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=300, default=None)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "user_song_comment"


class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField(Song, default=None)

    class Meta:
        db_table = "playlist"


class UserFavorites(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, default=None)
    artists = models.ManyToManyField(Artist, default=None)

    class Meta:
        db_table = "user_song_favorites"
