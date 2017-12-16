from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin

from learning_experience_submissions.models import LESubmission, LESubmissionRating, LESubmissionRatingMetrics
from learning_experience_submissions.permissions import IsAllowedOrSuperuser
from learning_experience_submissions.serializers import LESubmissionSerializer, LESubmissionRatingSerializer, \
    LESubmissionListSerializer


class LESubmissionViewSet(CreatedModifiedByModelViewSetMixin):

    queryset = LESubmission.objects.get_active()
    serializer_class = LESubmissionSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('title', 'description', 'markdown')

    permission_classes = (IsAllowedOrSuperuser, IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            self.queryset = self.queryset.filter(created_by=request.user)
        else:
            self.queryset = LESubmission.objects.get_with_have_rated(user_id=request.user.id)

        self.serializer_class = LESubmissionListSerializer

        return super(LESubmissionViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(LESubmissionViewSet, self).retrieve(request, *args, **kwargs)

    @detail_route(methods=['post',])
    def make_new_version(self, request, *args, **kwargs):
        instance = self.get_object()
        instance = instance.make_new_version()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(methods=['post',])
    def submit(self, request, *args, **kwargs):
        # id = kwargs.get('pk')
        # search_filter = {}
        # search_filter['id'] = id
        # if not (request.user.is_staff or request.user.is_superuser):
        #     search_filter['created_by_id'] = request.user.id
        #
        # instance = LESubmission.objects.get(**search_filter)
        instance = self.get_object()
        instance.submit()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if 'image_id' in request.data:
            if request.data['image_id'] is None:
                del request.data['image_id']

        return super(LESubmissionViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if 'image_id' in request.data:
            if request.data['image_id'] is None:
                del request.data['image_id']

        return super(LESubmissionViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance = instance.mark_as_deleted()
        return Response(status=HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        if 'image_id' in request.data:
            if request.data['image_id'] is None:
                del request.data['image_id']

        return super(LESubmissionViewSet, self).create(request, *args, **kwargs)


class LESubmissionRatingViewSet(CreatedModifiedByModelViewSetMixin):

    queryset = LESubmissionRating.objects.get_queryset()
    serializer_class = LESubmissionRatingSerializer

    permission_classes = (IsAllowedOrSuperuser, IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            self.queryset = self.queryset.filter(le_submission__created_by=request.user)

        return super(LESubmissionRatingViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(LESubmissionRatingViewSet, self).retrieve(request, *args, **kwargs)

    @list_route(methods=['get',])
    def metrics(self, request, *args, **kwargs):
        return Response(LESubmissionRatingMetrics)

    def update(self, request, *args, **kwargs):
        return super(LESubmissionRatingViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super(LESubmissionRatingViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(LESubmissionRatingViewSet, self).destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super(LESubmissionRatingViewSet, self).create(request, *args, **kwargs)

