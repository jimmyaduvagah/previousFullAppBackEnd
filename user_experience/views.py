import re
from django.db.models.query_utils import Q
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .models import UserProfileExperience, UserProfileExperienceType
from .permissions import IsAllowedOrSuperuser
from .serializers import UserProfileExperienceSerializer, UserProfileExperienceTypeSerializer, UserProfileExperienceFullSerializer, UserProfileExperienceTypeSelect2Serializer
from twz_server_django.rest_extensions import BaseModelViewSet, CreatedModifiedByModelViewSetMixin


class UserProfileExperienceViewSet(BaseModelViewSet, CreatedModifiedByModelViewSetMixin):

    queryset = UserProfileExperience.objects.all().order_by('-date_to', '-date_from')
    serializer_class = UserProfileExperienceSerializer
    full_serializer_class = UserProfileExperienceFullSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', None)
        if user_id is None or len(user_id) < 10:
            user_id = request.user.id

        self.queryset = self.queryset.filter(user_id=user_id)

        return super(UserProfileExperienceViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def jobs(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', None)
        if user_id is None or len(user_id) < 10:
            user_id = request.user.id
        q = Q(
            Q(Q(type_id='eac3313e-f22e-4301-9169-477aa4b8b313') | Q(type_id='8e12ea4c-c222-42db-acf1-e81fd7d768bd')) & Q(user_id=user_id)
        )
        self.queryset = self.queryset.filter(q)

        return super(UserProfileExperienceViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def education(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', None)
        if user_id is None or len(user_id) < 10:
            user_id = request.user.id
        self.queryset = self.queryset.filter(type_id='2df68ab6-5b76-4996-9a77-a62e07bc552d', user_id=user_id)

        return super(UserProfileExperienceViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        regex = re.compile('^[0-9][0-9]-[0-9][0-9][0-9][0-9]$')
        if request.data['date_from']:
            if regex.match(request.data['date_from']):
                request.data['date_from'] = "%s-01" % request.data['date_from']
        if request.data['date_to']:
            if regex.match(request.data['date_to']):
                request.data['date_to'] = "%s-01" % request.data['date_to']
        return super(UserProfileExperienceViewSet, self).create(request, *args, **kwargs)


class UserProfileExperienceTypeViewSet(BaseModelViewSet, CreatedModifiedByModelViewSetMixin):

    queryset = UserProfileExperienceType.objects.all()
    serializer_class = UserProfileExperienceTypeSerializer
    permission_classes = (IsAuthenticated,)
    select2_serializer_class = UserProfileExperienceTypeSelect2Serializer