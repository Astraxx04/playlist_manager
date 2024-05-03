from django.urls import path, include
from . import views

urlpatterns = [
    path('songs/', views.songs, name='songs'),
]