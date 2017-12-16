import datetime
import django_filters
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters

from attachments.models import Attachment
from module_progress.serializers_admin import ModuleProgressAdminSerializer
from .permissions import IsAllowedOrSuperuser
from attachments.serializers import AttachmentSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin, UserCreateForOwnUserPermission, \
    AdminViewSetMixin
from twz_server_django.utils import log_action
from module_progress.models import ModuleProgress
from module_progress.serializers import ModuleProgressSerializer

class ModuleProgressFilter(django_filters.FilterSet):
    # is_parent = django_filters.BooleanFilter(name='parent_media_id', lookup_expr="isnull")

    class Meta:
        model = ModuleProgress
        fields = [
            'user_id',
            'module_id',
            'current_media_id',
            'id',
            'user_id',
            'created_on',
            'assessment_submitted',
            'assessment_response_completed',
            'completed'
        ]


class ModuleProgressAdminViewSet(AdminViewSetMixin):
    queryset = ModuleProgress.objects.all()
    serializer_class = ModuleProgressAdminSerializer
    full_serializer_class = ModuleProgressAdminSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,filters.OrderingFilter,)
    filter_class = ModuleProgressFilter
    ordering_fields = (
        'id',
        'user__last_name',
        'module__title',
        'current_media__title',
        'created_on',
        'assessment_submitted',
        'assessment_response_completed',
        'completed'
    )

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

