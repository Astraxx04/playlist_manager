from rest_framework import serializers
from django.utils import timezone
from .models import Song
from .models import Playlist
from .models import PlaylistSong

class SongSerializer(serializers.ModelSerializer):
    def validate_data(self, data):
        name = data.get('name')
        artist = data.get('artist')
        release_year = data.get('release_year')

        current_year = timezone.now().year
        if release_year < 1900 or release_year > current_year:
            raise serializers.ValidationError("Invalid release year.")

        existing_songs = Song.objects.filter(name=name, artist=artist)
        if existing_songs.exists():
            raise serializers.ValidationError("A song with the same name and artist already exists.")

        return data

    class Meta:
        model = Song
        fields = ['id', 'name', 'artist', 'release_year']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name']

class PlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
        fields = ['playlist', 'song', 'position']
