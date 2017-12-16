import datetime
import django_filters
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters

from attachments.models import Attachment
from .permissions import IsAllowedOrSuperuser
from attachments.serializers import AttachmentSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin, UserCreateForOwnUserPermission
from twz_server_django.utils import log_action
from module_progress.models import ModuleProgress
from module_progress.serializers import ModuleProgressSerializer

class ModuleProgressFilter(django_filters.FilterSet):
    # is_parent = django_filters.BooleanFilter(name='parent_media_id', lookup_expr="isnull")

    class Meta:
        model = ModuleProgress
        fields = ['user_id', 'module_id', 'completed']

class ModuleProgressViewSet(CreatedModifiedByModelViewSetMixin, UserCreateForOwnUserPermission):
    queryset = ModuleProgress.objects.all()
    serializer_class = ModuleProgressSerializer
    full_serializer_class  = ModuleProgressSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)
    # pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ModuleProgressFilter

    @list_route()
    def get_or_create(self, request, *args, **kwargs):
        module_id = request.GET.get('module_id', None)
        if module_id:
            self.queryset = ModuleProgress.objects.get_for_user_and_module(request.user.id, module_id)
        else:
            raise NotAcceptable('Missing module_id')
        self.check_for_full_serializer(request)
        serializer = self.get_serializer(self.queryset)
        response = Response(serializer.data)
        return response

    @detail_route(methods=['get'])
    def files(self, request, *args, **kwargs):
        self.filter_backends = ()
        self.filter_class = None

        module_id = request.GET.get('module_id', None)
        if module_id:
            self.queryset = ModuleProgress.objects.get_for_user_and_module(request.user.id, module_id)
        else:
            self.queryset = ModuleProgress.objects.get(user_id=request.user.id, id=kwargs['pk'])
        attachments = Attachment.objects.get_attachments_for_object(self.queryset)

        serializer = AttachmentSerializer(attachments, many=True)
        response = Response(serializer.data)
        return response

    @detail_route(methods=['put'])
    def upload(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        obj = self.get_object()
        mime_type = ''
        #multipart form upload
        file = request.FILES.get('file', None)
        mime_type = file.content_type

        if file != None:
            attachment = Attachment.objects.save_attachment_for_object(
                obj=obj,
                file=file,
                mime_type=mime_type,
                request=request
            )

            # log_action(request, attachment)
            response = AttachmentSerializer(attachment)
            return Response(response.data, status=201)
        else:
            response = '{"detail":"No File"}'
            # log_action(request)
            return Response(response, status=406)

    @detail_route(methods=['put'])
    def completed(self, request, *args, **kwargs):
        self.filter_backends = ()
        self.queryset = self.queryset.filter(user=request.user)

        super(ModuleProgressViewSet, self).update(request, *args, **kwargs)
        instance = self.get_object()
        instance.assessment_submitted_on = datetime.datetime.now()
        instance.save()
        response = Response(ModuleProgressSerializer(instance).data, status=204)
        return response


    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        log_action(request)
        response = super(ModuleProgressViewSet, self).list(request, *args, **kwargs)
        return response

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)
        response = super(ModuleProgressViewSet, self).retrieve(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied()

    def update(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        # if kwargs.get('upload', None):
        #     response = self.upload_file(request, *args, **kwargs)
        # else:
        response = super(ModuleProgressViewSet, self).update(request, *args, **kwargs)

        return response

    def create(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        response = super(ModuleProgressViewSet, self).create(request, *args, **kwargs)
        return response
