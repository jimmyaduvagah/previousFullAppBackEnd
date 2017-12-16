import django_filters
from rest_framework import filters

from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from .models import ModuleCategory, Module
from .serializers import ModuleCategorySerializer, ModuleSerializer


class ModuleFilter(django_filters.FilterSet):
    ids = django_filters.CharFilter(method='filter_ids')

    def filter_ids(self, queryset, value):
        return queryset.filter(id__in=value.split(','))

    class Meta:
        model = Module
        fields = ['category_id', 'title', 'id']


class ModuleCategoryViewSet(CreatedModifiedByModelViewSetMixin):

    serializer_class = ModuleCategorySerializer
    queryset = ModuleCategory.objects.all()


class ModuleViewSet(CreatedModifiedByModelViewSetMixin):

    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ModuleFilter


