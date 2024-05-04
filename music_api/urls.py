from django.urls import path, include
from . import views

urlpatterns = [
    path('songs/', views.songs, name='songs'),
    path('playlists/', views.playlists, name='playlists'),
    path('playlists/<int:playlist_id>', views.playlist_operations, name='edit_playlist'),
    path('playlists/<int:playlist_id>/songs/', views.list_playlist_songs, name='list_playlist_songs'),
    path('playlists/<int:playlist_id>/songs/<song_id>', views.move_playlist_song, name='move_playlist_song'),
]