from rest_framework import serializers

from drf_users.serializers import UserSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2
from module_progress.models import ModuleProgress


class ModuleProgressAdminSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ModuleProgress
        fields = (
            'id',
            'modified_on',
            'created_on',
            'modified_by_id',
            'created_by_id',
            'modified_by',
            'created_by',
            'object',
            'completed',
            'percent_completed',
            'has_assessment',
            'assessment_submitted',
            'assessment_submitted_on',
            'assessment_response_completed',
            'module_id',
            'module',
            'current_media_id',
            'current_media',
            'user_id',
            'user'
        )

    current_media_id = serializers.UUIDField()
    current_media = serializers.CharField(source='current_media.title')
    user_id = serializers.UUIDField()
    user = UserSerializer()
    module_id = serializers.UUIDField()
    module = serializers.CharField(source='module.title')

