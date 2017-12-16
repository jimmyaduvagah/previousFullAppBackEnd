import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from tags.models import Tag
from tags.serializers import TagSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin


class TagViewset(CreatedModifiedByModelViewSetMixin):
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ('title',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, SearchFilter)

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data['created_by_id'] = str(request.user.id)
        data['modified_by_id'] = str(request.user.id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        to_return = None
        created = False
        tag = None
        try:
            tag = Tag.objects.get(title__iexact=serializer.data['title'])
        except (ObjectDoesNotExist) as e:
            created = True
            tag = serializer.create(serializer.data)

        headers = self.get_success_headers(serializer.data)
        response_status = status.HTTP_200_OK
        if created:
            response_status = status.HTTP_201_CREATED

        to_return = Response(self.get_serializer(tag).data, status=response_status, headers=headers)

        return to_return

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(TagViewset, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(TagViewset, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(TagViewset, self).partial_update(request, *args, **kwargs)

        raise MethodNotAllowed('PATCH')
