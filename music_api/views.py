from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import SongSerializer, PlaylistSerializer, PlaylistSongSerializer
from .models import Song, Playlist, PlaylistSong


class SongView(APIView):
    @swagger_auto_schema(
        operation_summary="List available songs",
        operation_description="This endpoint is used to list all the available songs in the app.",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page Number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Song Name",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success"
            )
        }
    )
    def get(self, request):
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


    @swagger_auto_schema(
        operation_summary="Create new song",
        operation_description="This endpoint is used to add a new song entry in the songs table.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example="Song1"),
                'artist': openapi.Schema(type=openapi.TYPE_STRING, example="Artist1"),
                'release_year': openapi.Schema(type=openapi.TYPE_INTEGER, example=2000),
            }
        ),
        responses={
            201: openapi.Response(
                description="Success. The song entry has been created."
            )
        },
    )
    def post(self, request):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Success. The song entry has been created.", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PlaylistView(APIView):
    @swagger_auto_schema(
        operation_summary="List available playlists",
        operation_description="This endpoint is used to list all the available playlists in the app.",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page Number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Playlist Name",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success"
            )
        }
    )
    def get(self, request):
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


    @swagger_auto_schema(
        operation_summary="Create new playlist",
        operation_description="This endpoint is used to add a new playlist entry in the playlists table.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example="Playlist1"),
                'songs': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[2,5,3,10,8])
            }
        ),
        responses={
            201: openapi.Response(
                description="Success. The playlist entry has been created."
            )
        },
    )
    def post(self, request):
        serializer = PlaylistSerializer(data=request.data)
        if serializer.is_valid():
            playlist = serializer.save()

            songs = request.data.get('songs', [])
            for position, song_id in enumerate(songs, start=1):
                song = Song.objects.get(pk=song_id)
                playlist_song_data = {'playlist': playlist.pk, 'song': song.pk, 'position': position}
                playlist_song_serializer = PlaylistSongSerializer(data=playlist_song_data)
                if playlist_song_serializer.is_valid():
                    playlist_song_serializer.save()
                else:
                    playlist.delete()
                    return Response(playlist_song_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response("Success. The playlist entry has been created.", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PlaylistModifyDeleteView(APIView):
    @swagger_auto_schema(
        operation_summary="Edit playlist metadata",
        operation_description="This endpoint is used to change the name of an existing playlist.",
        manual_parameters=[
            openapi.Parameter(
                'playlist_id',
                openapi.IN_PATH,
                description="Playlist Id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, example="Playlist1"),
            }
        ),
        responses={
            200: openapi.Response(
                description="Success. The name of the playlist has been edited."
            )
        },
    )
    def put(self, request, playlist_id):
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            return Response("Playlist not found", status=status.HTTP_404_NOT_FOUND)

        serializer = PlaylistSerializer(playlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Success. The name of the playlist has been edited.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="Delete playlist",
        operation_description="This endpoint is used to delete an existing playlist.",
        manual_parameters=[
            openapi.Parameter(
                'playlist_id',
                openapi.IN_PATH,
                description="Playlist Id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success. The playlist has been deleted."
            )
        },
    )
    def delete(self, request, playlist_id):
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            return Response("Playlist not found", status=status.HTTP_404_NOT_FOUND)

        playlist.delete()
        return Response("Success. The playlist has been deleted", status=status.HTTP_200_OK)



class ListPlaylistSongsView(APIView):
    @swagger_auto_schema(
        operation_summary="List playlist songs",
        operation_description="This endpoint is used to list all the songs associated with a playlist.",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page Number",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success"
            )
        }
    )
    def get(self, request, playlist_id):
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



class PlaylistMoveDeleteSongView(APIView):
    @swagger_auto_schema(
        operation_summary="Move playlist song",
        operation_description="This endpoint is used to move a song up and down in a playlist ie. reposition it.",
        manual_parameters=[
            openapi.Parameter(
                'playlist_id',
                openapi.IN_PATH,
                description="Playlist Id",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'song_id',
                openapi.IN_PATH,
                description="Song Id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'position': openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
            }
        ),
        responses={
            200: openapi.Response(
                description="Success. Song has been moved to the new position in the playlist."
            )
        },
    )
    def put(self, request, playlist_id, song_id):
        try:
            playlist_song = PlaylistSong.objects.get(playlist_id=playlist_id, song_id=song_id)
        except PlaylistSong.DoesNotExist:
            return Response("Playlist song not found", status=status.HTTP_404_NOT_FOUND)

        new_position = request.data.get('position')

        if new_position is None:
            return Response("Position is required", status=status.HTTP_400_BAD_REQUEST)

        song_count = PlaylistSong.objects.filter(playlist_id=playlist_id).count()

        if new_position < 1 or new_position > song_count:
            return Response("Position is invalid", status=status.HTTP_400_BAD_REQUEST)

        old_position = playlist_song.position

        songs_to_adjust = PlaylistSong.objects.filter(playlist_id=playlist_id, position__gte=min(old_position, new_position), position__lte=max(old_position, new_position)).exclude(id=playlist_song.id)

        for song in songs_to_adjust:
            if old_position < new_position:
                song.position -= 1
            else:
                song.position += 1
            song.save()

        playlist_song.position = new_position
        playlist_song.save()

        return Response("Success. Song has been moved to the new position in the playlist.", status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="Remove playlist song",
        operation_description="This endpoint is used to remove a song from a playlist.",
        manual_parameters=[
            openapi.Parameter(
                'playlist_id',
                openapi.IN_PATH,
                description="Playlist Id",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                'song_id',
                openapi.IN_PATH,
                description="Song Id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success. Song has been removed from the playlist."
            )
        },
    )
    def delete(self, request, playlist_id, song_id):
        try:
            playlist_song = PlaylistSong.objects.get(playlist_id=playlist_id, song_id=song_id)
        except PlaylistSong.DoesNotExist:
            return Response("Playlist song not found", status=status.HTTP_404_NOT_FOUND)

        songs_to_adjust = PlaylistSong.objects.filter(playlist_id=playlist_id, position__gt=playlist_song.position)

        for song in songs_to_adjust:
            song.position -= 1
            song.save()

        playlist_song.delete()

        return Response("Success. Song has been removed from the playlist.", status=status.HTTP_200_OK)