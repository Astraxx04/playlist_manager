from rest_framework import serializers
from django.utils import timezone
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    def validate_release_year(self, value):
        current_year = timezone.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError("Invalid release year")
        return value

    class Meta:
        model = Song
        fields = ['name', 'artist', 'release_year']