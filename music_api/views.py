from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from .serializers import SongSerializer
from .serializers import PlaylistSerializer
from .serializers import PlaylistSongSerializer
from .models import Song
from .models import Playlist
from .models import PlaylistSong

@api_view(['GET', 'POST'])
def songs(request):
    if request.method == 'GET':
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')

        songs = Song.objects.order_by('id')
        if search_query:
            songs = songs.filter(name__icontains=search_query)

        paginator = Paginator(songs, 10)
        page_obj = paginator.get_page(page_number)

        serializer = SongSerializer(page_obj.object_list, many=True)

        base_url = request.build_absolute_uri(reverse('songs'))

        response_data = {
            'count': paginator.count,
            'next': base_url + f'?page={page_obj.next_page_number()}' if page_obj.has_next() else None,
            'previous': base_url + f'?page={page_obj.previous_page_number()}' if page_obj.has_previous() else None,
            'results': serializer.data
        }
        return Response(response_data)

    elif request.method == 'POST':
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Success. The song entry has been created.", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def playlists(request):
    if request.method == 'GET':
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')

        playlists = Playlist.objects.order_by('id')
        if search_query:
            playlists = playlists.filter(name__icontains=search_query)

        paginator = Paginator(playlists, 10)
        page_obj = paginator.get_page(page_number)

        serializer = PlaylistSerializer(page_obj.object_list, many=True)

        base_url = request.build_absolute_uri(reverse('playlists'))

        response_data = {
            'count': paginator.count,
            'next': base_url + f'?page={page_obj.next_page_number()}' if page_obj.has_next() else None,
            'previous': base_url + f'?page={page_obj.previous_page_number()}' if page_obj.has_previous() else None,
            'results': serializer.data
        }
        return Response(response_data)

    elif request.method == 'POST':
        serializer = PlaylistSerializer(data=request.data)
    if serializer.is_valid():
        # Save the playlist first
        playlist = serializer.save()

        # Now, handle the songs
        songs = request.data.get('songs', [])
        for position, song_id in enumerate(songs, start=1):
            song = Song.objects.get(pk=song_id)
            playlist_song_data = {'playlist': playlist.pk, 'song': song.pk, 'position': position}
            playlist_song_serializer = PlaylistSongSerializer(data=playlist_song_data)
            if playlist_song_serializer.is_valid():
                playlist_song_serializer.save()
            else:
                # If the PlaylistSong data is invalid, delete the created playlist and return errors
                playlist.delete()
                return Response(playlist_song_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("Success. The playlist entry has been created.", status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def playlist_operations(request, playlist_id):
    try:
        playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist:
        return Response("Playlist not found", status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PlaylistSerializer(playlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Success. The name of the playlist has been edited.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        playlist.delete()
        return Response("Success. The playlist has been deleted", status=status.HTTP_200_OK)



@api_view(['GET'])
def list_playlist_songs(request, playlist_id):
    try:
        playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist:
        return Response("Playlist not found", status=status.HTTP_404_NOT_FOUND)

    page_number = request.GET.get('page', 1)

    playlist_songs = playlist.playlistsong_set.order_by('position')
    paginator = Paginator(playlist_songs, 10)
    page_obj = paginator.get_page(page_number)

    response_data = {
        'count': paginator.count,
        'next': None,
        'previous': None,
        'results': []
    }

    base_url = request.build_absolute_uri(reverse('list_playlist_songs', args=[playlist_id]))

    for playlist_song in page_obj.object_list:
        song_data = SongSerializer(playlist_song.song).data
        song_data['position'] = playlist_song.position
        response_data['results'].append(song_data)

    if page_obj.has_next():
        response_data['next'] = base_url + f'?page={page_obj.next_page_number()}'
    if page_obj.has_previous():
        response_data['previous'] = base_url + f'?page={page_obj.previous_page_number()}'

    return Response(response_data)


@api_view(['PUT', 'DELETE'])
def move_playlist_song(request, playlist_id, song_id):
    try:
        playlist_song = PlaylistSong.objects.get(playlist_id=playlist_id, song_id=song_id)
    except PlaylistSong.DoesNotExist:
        return Response("Playlist song not found", status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':

        new_position = request.data.get('position')

        if new_position is None:
            return Response("Position is required", status=status.HTTP_400_BAD_REQUEST)

        old_position = playlist_song.position

        # Get all songs in the same playlist with positions between old and new positions
        songs_to_adjust = PlaylistSong.objects.filter(playlist_id=playlist_id, position__gte=min(old_position, new_position), position__lte=max(old_position, new_position)).exclude(id=playlist_song.id)

        # Update positions of affected songs
        for song in songs_to_adjust:
            if old_position < new_position:
                song.position -= 1
            else:
                song.position += 1
            song.save()

        # Update position of the moved song
        playlist_song.position = new_position
        playlist_song.save()

        return Response("Success. Song has been moved to the new position in the playlist.", status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # Get all songs in the same playlist with positions greater than the position of the removed song
        songs_to_adjust = PlaylistSong.objects.filter(playlist_id=playlist_id, position__gt=playlist_song.position)

        # Update positions of affected songs
        for song in songs_to_adjust:
            song.position -= 1
            song.save()

        # Delete the playlist song
        playlist_song.delete()

        return Response("Success. Song has been removed from the playlist.", status=status.HTTP_200_OK)