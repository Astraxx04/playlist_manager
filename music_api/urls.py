from django.urls import path
from .views import SongView, PlaylistView, PlaylistModifyDeleteView, ListPlaylistSongsView, PlaylistMoveDeleteSongView
from . import views

urlpatterns = [
    path('songs', SongView.as_view(), name='songs'),
    path('playlists', PlaylistView.as_view(), name='playlists'),
    path('playlists/<int:playlist_id>', PlaylistModifyDeleteView.as_view(), name='edit_playlist'),
    path('playlists/<int:playlist_id>/songs', ListPlaylistSongsView.as_view(), name='list_playlist_songs'),
    path('playlists/<int:playlist_id>/songs/<song_id>', PlaylistMoveDeleteSongView.as_view(), name='move_playlist_song'),
]