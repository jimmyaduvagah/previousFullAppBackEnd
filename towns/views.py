# Create your views here.
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from towns.models import Town
from towns.serializers import TownSerializer
from twz_server_django.rest_extensions import SlugFilterListViewSet, CreateListRetrieveViewSet


class TownsViewSet(CreateListRetrieveViewSet, SlugFilterListViewSet):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ('name',)
    filter_backends = (SearchFilter, )