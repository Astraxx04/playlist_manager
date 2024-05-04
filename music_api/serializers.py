from rest_framework import serializers
from django.utils import timezone
from .models import Song
from .models import Playlist
from .models import PlaylistSong

class SongSerializer(serializers.ModelSerializer):
    def validate_release_year(self, value):
        current_year = timezone.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError("Invalid release year")
        return value

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

    # def create(self, validated_data):
    #     songs_data = validated_data.pop('songs', [])
    #     playlist = Playlist.objects.create(**validated_data)
    #     for song_data in songs_data:
    #         song = Song.objects.get_or_create(**song_data)[0]
    #         playlist.songs.add(song)
    #     return playlist

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.save()
    #     return instance

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['songs'] = SongSerializer(instance.songs.all(), many=True).data
    #     return representation