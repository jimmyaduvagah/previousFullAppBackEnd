import django_filters
from rest_framework.permissions import IsAuthenticated

from attachments.permissions import IsAllowedOrSuperuser
from reviews.models import ReviewTemplate, Review
from reviews.serializers import ReviewTemplateSerializer, ReviewSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin


class ReviewTemplateViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = ReviewTemplate.objects.all()
    serializer_class = ReviewTemplateSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    pagination_class = None


class ReviewFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Review
        fields = ['object_id', 'created_by']


class ReviewViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ReviewFilter
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    pagination_class = None
