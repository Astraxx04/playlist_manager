from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

# Create your views here.

@api_view(['GET'])
def hello(request):
    return HttpResponse("Hello world")