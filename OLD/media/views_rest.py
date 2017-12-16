import django_filters
from rest_framework import filters

from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from media.models import Media
from media.serializers import MediaSerializer


class MediaFilter(django_filters.FilterSet):

    class Meta:
        model = Media
        fields = ['module__category_id', 'title', 'module_id']

class MediaViewset(CreatedModifiedByModelViewSetMixin):

    serializer_class = MediaSerializer
    queryset = Media.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MediaFilter
