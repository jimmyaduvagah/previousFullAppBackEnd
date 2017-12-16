import os
from .permissions import IsAllowedOrSuperuser
from twz_server_django.utils import log_action
from rest_framework.permissions import IsAuthenticated
from twz_server_django.rest_extensions import LimitOffsetPagination, CreatedModifiedByModelViewSetMixin
from .models import Attachment
from .serializers_admin import AttachmentAdminSerializer

class AttachmentAdminViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentAdminSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser,)

