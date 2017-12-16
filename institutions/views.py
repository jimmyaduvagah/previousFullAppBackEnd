from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .models import Institution, InstitutionType
from .permissions import IsAllowedOrSuperuser
from .serializers import InstitutionSerializer, InstitutionTypeSerializer, InstitutionSelect2Serializer, InstitutionFullSerializer
from twz_server_django.rest_extensions import BaseModelViewSet, CreatedModifiedByModelViewSetMixin
from django.db.models import Q


class InstitutionViewSet(BaseModelViewSet, CreatedModifiedByModelViewSetMixin):

    queryset = Institution.objects.all().order_by('title')
    serializer_class = InstitutionSerializer
    select2_serializer_class = InstitutionSelect2Serializer
    full_serializer_class = InstitutionFullSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('title',)

    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        filter_title = request.GET.get('filter_title', None)
        filter_type = request.GET.get('filter_type', None)
        filter_type_id = request.GET.get('filter_type_id', None)

        if filter_title:
            self.queryset = self.queryset.filter(title__icontains=filter_title)

        if filter_type:
            self.queryset = self.queryset.filter(type__title=filter_type)

        if filter_type_id:
            self.queryset = self.queryset.filter(type_id=filter_type_id)


        return super(InstitutionViewSet, self).list(request, *args, **kwargs)


class InstitutionTypeViewSet(BaseModelViewSet):

    queryset = InstitutionType.objects.all()
    serializer_class = InstitutionTypeSerializer
    permission_classes = (IsAuthenticated,)