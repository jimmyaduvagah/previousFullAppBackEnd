from django.utils.text import slugify
from rest_framework import viewsets, mixins

# Create your views here.
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from .models import Nationality
from .serializers import NationalitySerializer
from twz_server_django.rest_extensions import SlugFilterListViewSet, CreateListRetrieveViewSet


class NationalitiesViewSet(CreateListRetrieveViewSet, SlugFilterListViewSet):
    queryset = Nationality.objects.all()
    serializer_class = NationalitySerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ('name',)
    filter_backends = (SearchFilter,)