from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from .serializers import SongSerializer
from .models import Song

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